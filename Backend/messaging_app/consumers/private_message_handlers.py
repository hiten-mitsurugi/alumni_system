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


class PrivateMessageHandlersMixin:
    """
    Mixin for private message sending and bumping handlers.
    """
    
    async def handle_send_message(self, data: Dict[str, Any]):
        """Handle sending a private message with optional reply."""
        await self.update_user_status(self.user, 'activity')
        
        # Extract and validate data
        receiver_id = data.get('receiver_id')
        content = data.get('content', '').strip()
        attachment_ids = data.get('attachment_ids', [])
        reply_to_id = data.get('reply_to_id')
        
        # Validation
        if not receiver_id:
            return await self.send_json({'error': 'receiver_id is required'})
        if not content and not attachment_ids:
            return await self.send_json({'error': 'Message content or attachments are required'})
        if receiver_id == self.user.id:
            return await self.send_json({'error': 'Cannot send message to yourself'})
            
        try:
            receiver = await database_sync_to_async(User.objects.get)(id=receiver_id)
            
            # Check blocking status
            is_blocked_by_receiver = await self._is_user_blocked(receiver, self.user)
            is_blocked_by_sender = await self._is_user_blocked(self.user, receiver)
            
            if is_blocked_by_receiver:
                return await self.send_json({
                    'error': 'You cannot send messages to this user. You have been blocked.',
                    'blocked': True,
                    'type': 'blocked_by_them'
                })
                
            if is_blocked_by_sender:
                return await self.send_json({
                    'error': 'You cannot send messages to a user you have blocked. Please unblock them first.',
                    'blocked': True,
                    'type': 'blocked_by_me'
                })
            
            # Check if conversation exists
            conversation_exists = await self._check_conversation_exists(receiver)
            
            if not conversation_exists:
                # Create message request for new conversation
                return await self._create_message_request(receiver, content)
                
            # Create and send message
            message = await self._create_private_message(receiver, content, reply_to_id)
            await self.attach_files_to_message(message, attachment_ids)
            
            # Serialize and broadcast
            serialized = await self.serialize_message(message)
            await self.broadcast_to_users(
                [self.user.id, receiver.id], 
                'chat_message', 
                {'message': serialized}
            )
            
            # 🔔 NOTIFICATION: Broadcast notification update to receiver
            await self.channel_layer.group_send(
                f'user_{receiver.id}',
                {
                    'type': 'notification_update',
                    'data': {
                        'action': 'increment',
                        'type': 'message'
                    }
                }
            )
            
            await self.send_json({'status': 'success', 'message': serialized})
            
        except User.DoesNotExist:
            await self.send_json({'error': 'Receiver not found'})
        except Exception as e:
            logger.error(f"Error sending message: {e}", exc_info=True)
            await self.send_json({'error': f'Failed to send message: {str(e)}'})

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

    async def _create_private_message(self, receiver, content: str, reply_to_id: Optional[str]):
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

    async def handle_bump_message(self, data: Dict[str, Any]):
        """Handle bumping a message - creates a new message referencing the original."""
        await self.update_user_status(self.user, 'activity')
        
        # Extract data
        original_message_id = data.get('original_message_id')
        receiver_id = data.get('receiver_id')
        
        # Validation
        if not original_message_id:
            return await self.send_json({'error': 'original_message_id is required'})
        if not receiver_id:
            return await self.send_json({'error': 'receiver_id is required'})
        if receiver_id == self.user.id:
            return await self.send_json({'error': 'Cannot bump message to yourself'})
            
        try:
            # Get receiver user
            try:
                receiver = await database_sync_to_async(User.objects.get)(id=receiver_id)
            except User.DoesNotExist:
                return await self.send_json({'error': 'Receiver not found'})
            
            # Check if conversation exists
            conversation_exists = await self._check_conversation_exists(receiver)
            if not conversation_exists:
                return await self.send_json({'error': 'No active conversation with this user'})
            
            # Create bump message
            bump_message = await self._create_bump_message(receiver, original_message_id)
            
            # Serialize and broadcast
            serialized = await self.serialize_message(bump_message)
            
            await self.broadcast_to_users(
                [self.user.id, receiver.id], 
                'chat_message', 
                {'message': serialized}
            )
            await self.send_json({'status': 'success', 'message': serialized})
            
        except ValueError as ve:
            logger.error(f"Validation error in bump: {ve}")
            await self.send_json({'error': str(ve)})
        except Exception as e:
            logger.error(f"Unexpected error bumping message: {e}")
            await self.send_json({'error': 'Failed to bump message'})

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