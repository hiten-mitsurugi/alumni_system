"""
Private message helper methods.
Contains async database operations for private chat functionality.
"""
import logging
from typing import Optional
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.db.models import Q

from ..models import Message, MessageRequest

logger = logging.getLogger(__name__)
User = get_user_model()


class PrivateMessageHelpersMixin:
    """Mixin containing private message helper methods."""
    
    async def _check_conversation_exists(self, receiver) -> bool:
        """Check if conversation exists between users."""
        @database_sync_to_async
        def _check():
            # Check for existing messages
            messages_exist = Message.objects.filter(
                (Q(sender=self.user) & Q(receiver=receiver)) |
                (Q(sender=receiver) & Q(receiver=self.user))
            ).exists()
            
            # Check for accepted requests
            requests_exist = MessageRequest.objects.filter(
                (Q(sender=self.user) & Q(receiver=receiver)) |
                (Q(sender=receiver) & Q(receiver=self.user)),
                accepted=True
            ).exists()
            
            return messages_exist or requests_exist
            
        return await _check()

    async def create_message_with_reply(self, receiver, content: str, reply_to_id: Optional[str]):
        """Create a private message with optional reply."""
        @database_sync_to_async
        def _create():
            # Get reply message if specified
            reply_to = None
            if reply_to_id:
                try:
                    reply_to = Message.objects.get(id=reply_to_id)
                except Message.DoesNotExist:
                    logger.warning(f"Reply message {reply_to_id} not found")
                    
            # Create message with all relationships
            message = Message.objects.create(
                sender=self.user,
                receiver=receiver,
                content=content,
                reply_to=reply_to
            )
            
            # Return with relationships loaded
            return Message.objects.select_related(
                'sender', 'receiver', 'reply_to', 'reply_to__sender'
            ).prefetch_related('attachments').get(id=message.id)
            
        return await _create()

    async def _create_message_request(self, receiver, content: str):
        """Create a message request for new conversation."""
        @database_sync_to_async
        def _create_request():
            # Check for existing pending request
            existing = MessageRequest.objects.filter(
                Q(sender=self.user, receiver=receiver) |
                Q(sender=receiver, receiver=self.user),
                accepted=False
            ).exists()
            
            if existing:
                return None
                
            return MessageRequest.objects.create(
                sender=self.user, 
                receiver=receiver, 
                content=content
            )
            
        request = await _create_request()
        
        if not request:
            return await self.send_json({'status': 'pending', 'message': 'Request already sent'})
            
        # Notify receiver
        await self.broadcast_to_users(
            [receiver.id], 
            'message_request', 
            {
                'message': {
                    'id': str(request.id),
                    'sender': {'id': self.user.id, 'first_name': self.user.first_name},
                    'content': content,
                    'timestamp': request.timestamp.isoformat()
                }
            }
        )
        
        # 🔔 NOTIFICATION: Broadcast notification update for message request
        await self.channel_layer.group_send(
            f'user_{receiver.id}',
            {
                'type': 'notification_update',
                'data': {
                    'action': 'increment',
                    'type': 'request'
                }
            }
        )
        
        await self.send_json({'status': 'pending', 'message': 'Message request sent'})

    async def _create_bump_message(self, receiver, original_message_id: str):
        """Create a bump message referencing the original message."""
        @database_sync_to_async
        def _create():
            try:
                # Get the original message - can be any message accessible to both users
                original_message = Message.objects.get(id=original_message_id)
                
                # Verify the message is part of the conversation between these users
                is_in_conversation = (
                    (original_message.sender == self.user and original_message.receiver == receiver) or
                    (original_message.sender == receiver and original_message.receiver == self.user)
                )
                
                if not is_in_conversation:
                    raise ValueError("Message not found in this conversation")
                
                # Create bump message with special content and reply relationship
                message = Message.objects.create(
                    sender=self.user,
                    receiver=receiver,
                    content="🔔 Bumped message",  # Special indicator for bump
                    reply_to=original_message
                )
                
                # Return with relationships loaded
                return Message.objects.select_related(
                    'sender', 'receiver', 'reply_to', 'reply_to__sender'
                ).prefetch_related('attachments').get(id=message.id)
                
            except Message.DoesNotExist:
                raise ValueError("Original message not found")
            except Exception as e:
                logger.error(f"Error creating bump message: {e}")
                raise
            
        return await _create()
