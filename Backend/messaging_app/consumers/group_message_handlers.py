"""
WebSocket consumer handlers for messaging functionality.
"""

import json
import logging
from typing import Optional, List, Dict, Any
from channels.db import database_sync_to_async
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Q

from messaging_app.models import Message, MessageRequest, GroupChat, MessageReaction, MessageRead, Attachment
from messaging_app.serializers import MessageSerializer

logger = logging.getLogger(__name__)
User = get_user_model()

from .mention_utils import create_mentions, send_mention_notifications

class GroupMessageHandlersMixin:
    """
    Mixin for group message sending and bumping handlers.
    """
    
    async def handle_group_message(self, data: Dict[str, Any]):
        """Send message to group with optional reply."""
        await self.update_user_status(self.user, 'activity')
        
        content = data.get('content', '').strip()
        attachment_ids = data.get('attachment_ids', [])
        reply_to_id = data.get('reply_to_id')
        
        if not content and not attachment_ids:
            return await self.send_json({'error': 'Message content or attachments are required'})
            
        try:
            @database_sync_to_async
            def _create_group_message():
                # Get reply message if specified
                reply_to = None
                if reply_to_id:
                    try:
                        reply_to = Message.objects.get(id=reply_to_id)
                    except Message.DoesNotExist:
                        pass
                        
                # Create group message
                message = Message.objects.create(
                    sender=self.user,
                    group=self.group,
                    content=content,
                    reply_to=reply_to
                )
                
                # Return with relationships
                return Message.objects.select_related(
                    'sender', 'group', 'reply_to', 'reply_to__sender'
                ).prefetch_related('attachments').get(id=message.id)
                
            message = await _create_group_message()
            await self.attach_files_to_message(message, attachment_ids)
            
            # 🔔 MENTIONS: Process @mentions in group messages
            mentioned_users = await create_mentions(message, content, self.group)
            if mentioned_users:
                logger.info(f"Created mentions for {len(mentioned_users)} users in group message {message.id}")
                await send_mention_notifications(self.channel_layer, mentioned_users, message, self.group)
            
            # 🚀 SPEED: Invalidate Redis caches after sending group message
            @database_sync_to_async
            def _invalidate_caches():
                from django.core.cache import cache
                
                # Clear group conversation caches for all members
                for member in self.group.members.all():
                    cache.delete(f"user_conversations_{member.id}")
                    # Clear group message cache for each member
                    cache.delete(f"group_messages_{self.group.id}_{member.id}")
                
                logger.info(f"🚀 Cache invalidated after group message sent to group {self.group.id}")
            
            await _invalidate_caches()
            
            # Serialize and broadcast to group
            serialized = await self.serialize_message(message)
            await self.channel_layer.group_send(
                self.group_name, 
                {'type': 'chat_message', 'message': serialized}
            )
            
            # Also notify each group member on their personal channel for unread counters/highlights
            try:
                from asgiref.sync import async_to_sync
                from channels.layers import get_channel_layer
                channel_layer = get_channel_layer()
                
                @database_sync_to_async
                def _member_ids():
                    return list(self.group.members.values_list('id', flat=True))
                
                members = await _member_ids()
                preview = {
                    'id': str(message.id),
                    'group': str(self.group.id),
                    'content': message.content,
                    'timestamp': message.timestamp.isoformat(),
                    'sender': {
                        'id': self.user.id,
                        'first_name': self.user.first_name,
                        'last_name': self.user.last_name,
                    }
                }
                for member_id in members:
                    # Skip sender if you prefer not to increment their unread
                    if member_id == self.user.id:
                        continue
                    async_to_sync(channel_layer.group_send)(
                        f'user_{member_id}',
                        {
                            'type': 'group_message_preview',
                            'message': preview
                        }
                    )
                    # Send notification update for navbar badge
                    async_to_sync(channel_layer.group_send)(
                        f'user_{member_id}',
                        {
                            'type': 'notification_update',
                            'data': {
                                'action': 'increment',
                                'type': 'message'
                            }
                        }
                    )
            except Exception as notify_err:
                logger.error(f"Failed to send group message preview notifications: {notify_err}")
            
        except Exception as e:
            logger.error(f"Error sending group message: {e}", exc_info=True)
            await self.send_json({'error': f'Failed to send group message: {str(e)}'})

    async def handle_group_bump(self, data: Dict[str, Any]):
        """Handle bumping a message in group chat."""
        await self.update_user_status(self.user, 'activity')
        
        # Extract data
        original_message_id = data.get('original_message_id')
        
        # Validation
        if not original_message_id:
            return await self.send_json({'error': 'original_message_id is required'})
            
        try:
            @database_sync_to_async
            def _create_group_bump():
                # Get the original message - must be sender's own message in this group
                try:
                    original_message = Message.objects.get(
                        id=original_message_id,
                        sender=self.user,
                        group_id=self.group_id
                    )
                except Message.DoesNotExist:
                    raise ValueError("Original message not found or not owned by sender")
                
                # Create bump message
                message = Message.objects.create(
                    sender=self.user,
                    group=self.group,
                    content="🔔 Bumped message",  # Special indicator for bump
                    reply_to=original_message
                )
                
                # Return with relationships
                return Message.objects.select_related(
                    'sender', 'group', 'reply_to', 'reply_to__sender'
                ).prefetch_related('attachments').get(id=message.id)
                
            message = await _create_group_bump()
            
            # Serialize and broadcast to group
            serialized = await self.serialize_message(message)
            await self.channel_layer.group_send(
                self.group_name, 
                {'type': 'chat_message', 'message': serialized}
            )
            
        except ValueError as e:
            await self.send_json({'error': str(e)})
        except Exception as e:
            logger.error(f"Error bumping group message: {e}")
            await self.send_json({'error': 'Failed to bump message'})