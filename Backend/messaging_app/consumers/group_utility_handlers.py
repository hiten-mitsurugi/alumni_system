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


class GroupUtilityHandlersMixin:
    """
    Mixin for group message utility handlers (pin, typing, read).
    """
    
    async def handle_group_pin(self, data: Dict[str, Any]):
        """Pin or unpin group message (any group member can pin)."""
        message_id = data.get('message_id')
        
        if not message_id:
            return await self.send_json({'error': 'message_id is required'})
            
        try:
            @database_sync_to_async
            def _pin():
                from django.utils import timezone as tz
                message = Message.objects.get(
                    id=message_id, 
                    group_id=self.group_id
                )
                
                # Toggle pin status
                message.is_pinned = not message.is_pinned
                message.save()
                return message.is_pinned
                
            is_pinned = await _pin()
            
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'message_pinned',
                    'message_id': str(message_id),
                    'is_pinned': is_pinned,
                    'action': 'pin' if is_pinned else 'unpin'
                }
            )
            
            # Send success confirmation to sender
            await self.send_json({
                'status': 'success', 
                'action': 'message_pinned',
                'message_id': str(message_id),
                'is_pinned': is_pinned
            })
            
        except Message.DoesNotExist:
            await self.send_json({'error': 'Message not found in this group'})
        except Exception as e:
            logger.error(f"Error pinning group message: {e}")
            await self.send_json({'error': 'Failed to pin message'})

    async def handle_group_typing(self, data: Dict[str, Any]):
        """Notify group of typing."""
        await self.channel_layer.group_send(
            self.group_name, 
            {'type': 'user_typing', 'user_id': self.user.id}
        )

    async def handle_group_stop_typing(self, data: Dict[str, Any]):
        """Notify group of stop typing."""
        await self.channel_layer.group_send(
            self.group_name, 
            {'type': 'user_stop_typing', 'user_id': self.user.id}
        )

    async def handle_group_mark_as_read(self, data: Dict[str, Any]):
        """Mark group messages as read for the current user."""
        group_id = data.get('group_id')
        
        if not group_id or str(group_id) != str(self.group_id):
            return
            
        @database_sync_to_async
        def _mark_group_read():
            # Get all unread messages in this group from other users
            unread_messages = Message.objects.filter(
                group_id=group_id
            ).exclude(sender=self.user)
            
            marked_count = 0
            # Only mark messages as read that don't already have a MessageRead record
            for message in unread_messages:
                msg_read_obj, created = MessageRead.objects.get_or_create(
                    message=message,
                    user=self.user,
                    defaults={'read_at': timezone.now()}
                )
                if created:
                    marked_count += 1
            
            return marked_count
            
        marked_count = await _mark_group_read()
        
        # 🔔 NOTIFICATION: Send notification update to decrement unread count
        if marked_count > 0:
            await self.channel_layer.group_send(
                f'user_{self.user.id}',
                {
                    'type': 'notification_update',
                    'data': {
                        'action': 'decrement',
                        'type': 'message',
                        'count': marked_count
                    }
                }
            )
            
            # Also invalidate cache for this user
            from django.core.cache import cache
            cache.delete(f"unread_counts_{self.user.id}")
        
        # Notify other group members that this user has read messages
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'group_messages_read',
                'user_id': self.user.id,
                'group_id': str(group_id)
            }
        )