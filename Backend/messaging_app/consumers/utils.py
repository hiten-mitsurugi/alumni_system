"""
Utility functions and global state for WebSocket messaging consumers.
Handles @mentions parsing/creation and active connection tracking.
"""
import re
import logging
from typing import Optional, List, Dict
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()

# Track active connections per user (shared global state)
ACTIVE_CONNECTIONS = {}


def parse_mentions(content: str) -> List[str]:
    """
    Parse @mentions from message content.
    Returns list of mentioned usernames.
    """
    # Match @username patterns (alphanumeric, underscore, dot, hyphen)
    mention_pattern = r'@([a-zA-Z0-9._-]+)'
    mentions = re.findall(mention_pattern, content)
    return mentions


async def create_mentions(message, content: str, group: Optional['GroupChat'] = None):
    """
    Create MessageMention objects for users mentioned in the message.
    Only works for group messages - private messages don't support mentions.
    """
    if not group:
        return []  # Only group messages support mentions
    
    mentioned_usernames = parse_mentions(content)
    if not mentioned_usernames:
        return []
    
    @database_sync_to_async
    def _create_mentions():
        from ..models import MessageMention
        created_mentions = []
        
        # Get group members that match the mentioned usernames
        mentioned_users = User.objects.filter(
            username__in=mentioned_usernames,
            group_chats=group  # Only group members can be mentioned
        ).exclude(id=message.sender.id)  # Don't mention yourself
        
        for user in mentioned_users:
            mention, created = MessageMention.objects.get_or_create(
                message=message,
                mentioned_user=user
            )
            if created:
                created_mentions.append({
                    'user_id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                })
        
        return created_mentions
    
    return await _create_mentions()


async def send_mention_notifications(channel_layer, mentioned_users: List[Dict], message, group: 'GroupChat'):
    """
    Send mention notifications to mentioned users.
    """
    for user_data in mentioned_users:
        user_id = user_data['user_id']
        
        # Send mention notification to the mentioned user
        await channel_layer.group_send(
            f'user_{user_id}',
            {
                'type': 'mention_notification',
                'data': {
                    'message_id': str(message.id),
                    'sender': {
                        'id': message.sender.id,
                        'username': message.sender.username,
                        'first_name': message.sender.first_name,
                        'last_name': message.sender.last_name
                    },
                    'group': {
                        'id': str(group.id),
                        'name': group.name
                    },
                    'content': message.content[:100] + '...' if len(message.content) > 100 else message.content,
                    'timestamp': message.timestamp.isoformat()
                }
            }
        )
