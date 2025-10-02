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


class GroupReactionHandlersMixin:
    """
    Mixin for group message reaction handlers.
    """
    
    async def handle_group_reaction(self, data: Dict[str, Any]):
        """Add or update reaction to group message (Facebook-style)."""
        message_id = data.get('message_id')
        reaction_type = data.get('reaction_type')
        
        if not message_id or not reaction_type:
            return await self.send_json({'error': 'message_id and reaction_type are required'})
            
        try:
            @database_sync_to_async
            def _add_reaction():
                from messaging_app.models import MessageReaction
                
                # Validate reaction type
                valid_reactions = dict(MessageReaction.REACTION_CHOICES).keys()
                if reaction_type not in valid_reactions:
                    raise ValueError(f'Invalid reaction type. Valid types: {list(valid_reactions)}')
                
                message = Message.objects.get(id=message_id, group_id=self.group_id)
                
                # Check if user is a member of the group
                if not message.group.members.filter(id=self.user.id).exists():
                    raise PermissionError('You are not a member of this group')
                
                # Add or update reaction
                reaction, created = MessageReaction.objects.update_or_create(
                    user=self.user,
                    message=message,
                    defaults={'reaction_type': reaction_type}
                )
                
                return message, reaction, created
                
            message, reaction, created = await _add_reaction()
            
            # Get updated reaction statistics
            @database_sync_to_async
            def _get_reaction_stats():
                from django.db.models import Count
                from messaging_app.models import MessageReaction
                
                reaction_counts = MessageReaction.objects.filter(
                    message=message
                ).values('reaction_type', 'emoji').annotate(
                    count=Count('id')
                ).order_by('-count')
                
                reactions_by_type = {}
                for reaction_type_info in MessageReaction.REACTION_CHOICES:
                    rt = reaction_type_info[0]
                    reactions = MessageReaction.objects.filter(
                        message=message,
                        reaction_type=rt
                    ).select_related('user')
                    
                    if reactions.exists():
                        reactions_by_type[rt] = {
                            'emoji': reaction_type_info[1],
                            'count': reactions.count(),
                            'users': [
                                {
                                    'id': r.user.id,
                                    'name': f"{r.user.first_name} {r.user.last_name}".strip() or r.user.username
                                }
                                for r in reactions
                            ]
                        }
                
                return {
                    'total_reactions': MessageReaction.objects.filter(message=message).count(),
                    'reaction_counts': list(reaction_counts),
                    'reactions_by_type': reactions_by_type
                }
            
            reaction_stats = await _get_reaction_stats()
            
            # Broadcast to group members
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'message_reaction',
                    'message_id': str(message.id),
                    'user_id': str(self.user.id),
                    'user_name': f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username,
                    'reaction_type': reaction_type,
                    'emoji': reaction.emoji,
                    'action': 'updated' if not created else 'added',
                    'reaction_stats': reaction_stats,
                    'timestamp': timezone.now().isoformat(),
                }
            )
            
            # Send confirmation to sender
            await self.send_json({
                'action': 'reaction_added',
                'success': True,
                'reaction': {
                    'id': str(reaction.id),
                    'reaction_type': reaction.reaction_type,
                    'emoji': reaction.emoji,
                    'created': created
                },
                'reaction_stats': reaction_stats
            })
            
        except ValueError as e:
            await self.send_json({'error': str(e)})
        except PermissionError as e:
            await self.send_json({'error': str(e)})
        except Message.DoesNotExist:
            await self.send_json({'error': 'Message not found'})