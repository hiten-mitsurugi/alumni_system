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


class PrivateUtilityHandlersMixin:
    """
    Mixin for private message utility handlers (pin, read, typing).
    """
    
    async def handle_pin_message(self, data: Dict[str, Any]):
        """Pin or unpin user's own message or messages in conversation."""
        message_id = data.get('message_id')
        
        logger.info(f"Pin request: message_id={message_id}, user={self.user.id}")
        
        if not message_id:
            logger.warning(f"Pin validation failed: message_id={message_id}")
            return await self.send_json({'error': 'message_id is required'})
            
        try:
            @database_sync_to_async
            def _pin():
                from django.utils import timezone as tz
                logger.info(f"Looking for message with id={message_id}")
                
                # Get the message - allow pinning for conversation participants
                message = Message.objects.get(id=message_id)
                
                # Check permissions
                can_pin = False
                if message.receiver:  # Private message
                    if self.user == message.sender or self.user == message.receiver:
                        can_pin = True
                elif message.group:  # Group message
                    if self.user in message.group.members.all():
                        can_pin = True
                
                if not can_pin:
                    raise PermissionError("No permission to pin this message")
                
                logger.info(f"Found message: {message.id}, current pin status: {message.is_pinned}")
                
                # Toggle pin status
                message.is_pinned = not message.is_pinned
                message.save()
                
                logger.info(f"Message pin status updated to: {message.is_pinned}")
                
                # Get user IDs for broadcasting - must be done in sync context
                if message.receiver:
                    users = [message.sender.id, message.receiver.id]
                else:
                    # For group messages, get all group members
                    users = list(message.group.members.values_list('id', flat=True))
                
                return message, message.is_pinned, users
                
            message, is_pinned, users = await _pin()
            
            # Broadcast to participants
            logger.info(f"Broadcasting pin update to users: {users}")
            await self.broadcast_to_users(
                users,
                'message_pinned',
                {
                    'message_id': str(message.id), 
                    'is_pinned': is_pinned,
                    'action': 'pin' if is_pinned else 'unpin'
                }
            )
            
            # Send success confirmation to sender
            await self.send_json({
                'status': 'success', 
                'action': 'message_pinned',
                'message_id': str(message.id),
                'is_pinned': is_pinned
            })
            logger.info(f"Pin completed successfully for message {message.id}")
            
        except Message.DoesNotExist:
            logger.error(f"Message not found: id={message_id}")
            await self.send_json({'error': 'Message not found'})
        except PermissionError as e:
            logger.error(f"Permission denied for pin: {e}")
            await self.send_json({'error': 'You do not have permission to pin this message'})
        except Exception as e:
            logger.error(f"Error pinning message {message_id}: {e}", exc_info=True)
            await self.send_json({'error': 'Failed to pin message'})

    async def handle_mark_as_read(self, data: Dict[str, Any]):
        """Mark messages from specific user as read."""
        receiver_id = data.get('receiver_id')
        
        if not receiver_id:
            return
            
        @database_sync_to_async
        def _mark_read():
            # Count how many messages will be marked as read
            unread_count = Message.objects.filter(
                sender_id=receiver_id, 
                receiver=self.user, 
                is_read=False
            ).count()
            
            # Mark messages as read
            Message.objects.filter(
                sender_id=receiver_id, 
                receiver=self.user, 
                is_read=False
            ).update(is_read=True)
            
            return unread_count
            
        marked_count = await _mark_read()
        
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
        
        await self.broadcast_to_users(
            [receiver_id], 
            'messages_read', 
            {'receiver_id': str(self.user.id)}
        )

    async def handle_typing(self, data: Dict[str, Any]):
        """Notify typing status."""
        receiver_id = data.get('receiver_id')
        if receiver_id:
            await self.broadcast_to_users(
                [receiver_id], 
                'user_typing', 
                {'user_id': self.user.id}
            )

    async def handle_stop_typing(self, data: Dict[str, Any]):
        """Notify stop typing."""
        receiver_id = data.get('receiver_id')
        if receiver_id:
            await self.broadcast_to_users(
                [receiver_id], 
                'user_stop_typing', 
                {'user_id': self.user.id}
            )