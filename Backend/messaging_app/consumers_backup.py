"""
Clean, well-documented WebSocket consumers for messaging functionality.
Handles private messages and group chats with reply threading support.
"""

import json
import logging
from typing import Optional, List, Dict, Any
from channels.generic.websocket import AsyncWebsocketConsumer, AsyncJsonWebsocketConsumer
from rest_framework_simplejwt.tokens import AccessToken, TokenError
from django.contrib.auth import get_user_model
from django.db.models import Q
from channels.db import database_sync_to_async
from django.utils import timezone

from messaging_app.models import Message, MessageRequest, GroupChat, Reaction, Attachment
from messaging_app.serializers import MessageSerializer

logger = logging.getLogger(__name__)
User = get_user_model()


class MessagingBaseMixin:
    """
    Base mixin providing common functionality for all messaging consumers.
    Handles authentication, user status updates, and message serialization.
    """
    
    async def authenticate_user(self) -> Optional[User]:
        """Extract and validate user from JWT token in query string."""
        try:
            query_string = self.scope['query_string'].decode()
            token = query_string.split('token=')[1] if 'token=' in query_string else None
            
            if not token:
                return None
                
            user_id = AccessToken(token)['user_id']
            return await database_sync_to_async(User.objects.get)(id=user_id)
            
        except (TokenError, User.DoesNotExist, IndexError):
            return None

    async def update_user_status(self, user: User, status: str) -> None:
        """Update user's online status and last seen timestamp."""
        @database_sync_to_async
        def _update_status():
            try:
                from auth_app.models import Profile
                profile, created = Profile.objects.get_or_create(user=user)
                
                if status == 'online':
                    profile.status = 'online'
                    profile.last_seen = timezone.now()
                elif status == 'activity':
                    # Keep current status, just update last_seen
                    profile.last_seen = timezone.now()
                    
                profile.save()
                logger.debug(f"Updated user {user.id} status: {status}")
                
            except Exception as e:
                logger.error(f"Error updating user status: {e}")
                
        await _update_status()

    async def serialize_message(self, message: Message) -> Dict[str, Any]:
        """Serialize message for WebSocket transmission with proper UUID handling."""
        @database_sync_to_async
        def _serialize():
            # Create mock request for URL building
            from django.http import HttpRequest
            mock_request = HttpRequest()
            mock_request.META = {'HTTP_HOST': '127.0.0.1:8000', 'wsgi.url_scheme': 'http'}
            
            serializer = MessageSerializer(message, context={'request': mock_request})
            data = serializer.data
            
            # Convert UUIDs to strings for JSON serialization
            if data.get('id'):
                data['id'] = str(data['id'])
            if data.get('reply_to') and data['reply_to'].get('id'):
                data['reply_to']['id'] = str(data['reply_to']['id'])
                
            return data
            
        return await _serialize()

    async def attach_files_to_message(self, message: Message, attachment_ids: List[str]) -> None:
        """Attach uploaded files to a message."""
        if not attachment_ids:
            return
            
        @database_sync_to_async
        def _attach_files():
            attachments = Attachment.objects.filter(id__in=attachment_ids)
            message.attachments.set(attachments)
            
        await _attach_files()

    async def broadcast_to_users(self, user_ids: List[int], event_type: str, payload: Dict[str, Any]) -> None:
        """Send the same event to multiple users."""
        for uid in set(user_ids):  # Remove duplicates
            await self.channel_layer.group_send(
                f'user_{uid}', 
                {'type': event_type, **payload}
            )

    async def send_json(self, data: Dict[str, Any]) -> None:
        """Send JSON data to client."""
        await self.send(text_data=json.dumps(data))


class PrivateChatConsumer(MessagingBaseMixin, AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for private messaging between two users.
    Handles message sending, reactions, editing, deletion, and read receipts.
    """
    
    async def connect(self):
        """Authenticate user and establish WebSocket connection."""
        self.user = await self.authenticate_user()
        if not self.user:
            await self.close()
            return
            
        # Set user online and join personal channel
        await self.update_user_status(self.user, 'online')
        self.user_group = f'user_{self.user.id}'
        await self.channel_layer.group_add(self.user_group, self.channel_name)
        await self.channel_layer.group_add('status_updates', self.channel_name)
        
        await self.accept()
        await self.send_json({'status': 'connected'})
        logger.info(f"User {self.user.id} connected to private chat")

    async def disconnect(self, close_code):
        """Clean up on disconnect - update activity but don't set offline."""
        if hasattr(self, 'user') and self.user:
            await self.update_user_status(self.user, 'activity')
            
        # Leave groups
        if hasattr(self, 'user_group'):
            await self.channel_layer.group_discard(self.user_group, self.channel_name)
        await self.channel_layer.group_discard('status_updates', self.channel_name)
        
        logger.info(f"User {getattr(self, 'user', {}).get('id', 'unknown')} disconnected")

    async def receive(self, text_data):
        """Route incoming messages to appropriate handlers."""
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            # Action routing map
            handlers = {
                'send_message': self.handle_send_message,
                'add_reaction': self.handle_add_reaction,
                'edit_message': self.handle_edit_message,
                'delete_message': self.handle_delete_message,
                'mark_as_read': self.handle_mark_as_read,
                'typing': self.handle_typing,
                'stop_typing': self.handle_stop_typing
            }
            
            handler = handlers.get(action)
            if handler:
                await handler(data)
            else:
                await self.send_json({'error': f'Unknown action: {action}'})
                
        except json.JSONDecodeError:
            await self.send_json({'error': 'Invalid JSON'})
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await self.send_json({'error': 'Server error'})

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
            await self.send_json({'status': 'success', 'message': serialized})
            
        except User.DoesNotExist:
            await self.send_json({'error': 'Receiver not found'})
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            await self.send_json({'error': 'Failed to send message'})

    async def _check_conversation_exists(self, receiver: User) -> bool:
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

    async def _create_message_request(self, receiver: User, content: str):
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
        
        await self.send_json({'status': 'pending', 'message': 'Message request sent'})

    async def _create_private_message(self, receiver: User, content: str, reply_to_id: Optional[str]) -> Message:
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

    async def handle_add_reaction(self, data: Dict[str, Any]):
        """Add emoji reaction to a message."""
        message_id = data.get('message_id')
        emoji = data.get('emoji')
        
        if not message_id or not emoji:
            return await self.send_json({'error': 'message_id and emoji are required'})
            
        try:
            @database_sync_to_async
            def _add_reaction():
                message = Message.objects.get(id=message_id)
                Reaction.objects.create(message=message, user=self.user, emoji=emoji)
                return message
                
            message = await _add_reaction()
            
            # Broadcast to both users
            users = [message.sender.id, message.receiver.id] if message.receiver else [message.sender.id]
            await self.broadcast_to_users(
                users, 
                'reaction_added',
                {
                    'message_id': str(message.id), 
                    'user_id': str(self.user.id), 
                    'emoji': emoji
                }
            )
            
        except Message.DoesNotExist:
            await self.send_json({'error': 'Message not found'})

    async def handle_edit_message(self, data: Dict[str, Any]):
        """Edit user's own message."""
        message_id = data.get('message_id')
        new_content = data.get('new_content', '').strip()
        
        if not message_id or not new_content:
            return await self.send_json({'error': 'message_id and new_content are required'})
            
        try:
            @database_sync_to_async
            def _edit():
                message = Message.objects.get(id=message_id, sender=self.user)
                message.content = new_content
                message.save()
                return message
                
            message = await _edit()
            
            # Broadcast to participants
            users = [message.sender.id, message.receiver.id] if message.receiver else [message.sender.id]
            await self.broadcast_to_users(
                users,
                'message_edited',
                {'message_id': str(message.id), 'new_content': new_content}
            )
            
        except Message.DoesNotExist:
            await self.send_json({'error': 'Cannot edit this message'})

    async def handle_delete_message(self, data: Dict[str, Any]):
        """Delete user's own message."""
        message_id = data.get('message_id')
        
        if not message_id:
            return await self.send_json({'error': 'message_id is required'})
            
        try:
            @database_sync_to_async
            def _delete():
                message = Message.objects.get(id=message_id, sender=self.user)
                users = [message.sender.id, message.receiver.id] if message.receiver else [message.sender.id]
                message.delete()
                return users
                
            users = await _delete()
            
            await self.broadcast_to_users(
                users,
                'message_deleted',
                {'message_id': str(message_id)}
            )
            
        except Message.DoesNotExist:
            await self.send_json({'error': 'Cannot delete this message'})

    async def handle_mark_as_read(self, data: Dict[str, Any]):
        """Mark messages from specific user as read."""
        receiver_id = data.get('receiver_id')
        
        if not receiver_id:
            return
            
        @database_sync_to_async
        def _mark_read():
            Message.objects.filter(
                sender_id=receiver_id, 
                receiver=self.user, 
                is_read=False
            ).update(is_read=True)
            
        await _mark_read()
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

    # Event handlers for broadcasts
    async def chat_message(self, event): 
        await self.send_json({'type': 'chat_message', **event})
    async def message_request(self, event): 
        await self.send_json({'type': 'message_request', **event})
    async def reaction_added(self, event): 
        await self.send_json({'type': 'reaction_added', **event})
    async def message_edited(self, event): 
        await self.send_json({'type': 'message_edited', **event})
    async def message_deleted(self, event): 
        await self.send_json({'type': 'message_deleted', **event})
    async def messages_read(self, event): 
        await self.send_json({'type': 'messages_read', **event})
    async def user_typing(self, event): 
        await self.send_json({'type': 'user_typing', **event})
    async def user_stop_typing(self, event): 
        await self.send_json({'type': 'user_stop_typing', **event})
    async def status_update(self, event): 
        await self.send_json({'type': 'status_update', **event})


class GroupChatConsumer(MessagingBaseMixin, AsyncWebsocketConsumer):
    """
    WebSocket consumer for group messaging.
    Handles group message sending, reactions, editing, and deletion.
    """
    
    async def connect(self):
        """Authenticate user and join group chat."""
        self.group_id = self.scope['url_route']['kwargs']['group_id']
        self.user = await self.authenticate_user()
        
        if not self.user:
            return await self.close()
            
        try:
            # Verify user is group member
            @database_sync_to_async
            def _check_membership():
                group = GroupChat.objects.get(id=self.group_id)
                return self.user in group.members.all(), group
                
            is_member, self.group = await _check_membership()
            
            if not is_member:
                return await self.close()
                
            # Set user online and join group
            await self.update_user_status(self.user, 'online')
            self.group_name = f'group_{self.group_id}'
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.channel_layer.group_add('status_updates', self.channel_name)
            
            await self.accept()
            await self.send_json({'status': 'connected'})
            logger.info(f"User {self.user.id} joined group {self.group_id}")
            
        except GroupChat.DoesNotExist:
            await self.close()

    async def disconnect(self, close_code):
        """Clean up on disconnect."""
        if hasattr(self, 'user') and self.user:
            await self.update_user_status(self.user, 'activity')
            
        # Leave groups
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.channel_layer.group_discard('status_updates', self.channel_name)
        
        logger.info(f"User {getattr(self, 'user', {}).get('id', 'unknown')} left group")

    async def receive(self, text_data):
        """Route group message actions."""
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            handlers = {
                'send_message': self.handle_group_message,
                'add_reaction': self.handle_group_reaction,
                'edit_message': self.handle_group_edit,
                'delete_message': self.handle_group_delete,
                'typing': self.handle_group_typing,
                'stop_typing': self.handle_group_stop_typing
            }
            
            handler = handlers.get(action)
            if handler:
                await handler(data)
            else:
                await self.send_json({'error': f'Unknown action: {action}'})
                
        except json.JSONDecodeError:
            await self.send_json({'error': 'Invalid JSON'})

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
            
            # Serialize and broadcast to group
            serialized = await self.serialize_message(message)
            await self.channel_layer.group_send(
                self.group_name, 
                {'type': 'chat_message', 'message': serialized}
            )
            
        except Exception as e:
            logger.error(f"Error sending group message: {e}")
            await self.send_json({'error': 'Failed to send message'})

    async def handle_group_reaction(self, data: Dict[str, Any]):
        """Add reaction to group message."""
        message_id = data.get('message_id')
        emoji = data.get('emoji')
        
        if not message_id or not emoji:
            return await self.send_json({'error': 'message_id and emoji are required'})
            
        try:
            @database_sync_to_async
            def _add_reaction():
                message = Message.objects.get(id=message_id, group_id=self.group_id)
                Reaction.objects.create(message=message, user=self.user, emoji=emoji)
                return message
                
            await _add_reaction()
            
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'reaction_added',
                    'message_id': str(message_id),
                    'user_id': str(self.user.id),
                    'emoji': emoji
                }
            )
            
        except Message.DoesNotExist:
            await self.send_json({'error': 'Message not found'})

    async def handle_group_edit(self, data: Dict[str, Any]):
        """Edit group message (own messages only)."""
        message_id = data.get('message_id')
        new_content = data.get('new_content', '').strip()
        
        if not message_id or not new_content:
            return await self.send_json({'error': 'message_id and new_content are required'})
            
        try:
            @database_sync_to_async
            def _edit():
                message = Message.objects.get(
                    id=message_id, 
                    group_id=self.group_id, 
                    sender=self.user
                )
                message.content = new_content
                message.save()
                
            await _edit()
            
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'message_edited',
                    'message_id': str(message_id),
                    'new_content': new_content
                }
            )
            
        except Message.DoesNotExist:
            await self.send_json({'error': 'Cannot edit this message'})

    async def handle_group_delete(self, data: Dict[str, Any]):
        """Delete group message (own messages only)."""
        message_id = data.get('message_id')
        
        if not message_id:
            return await self.send_json({'error': 'message_id is required'})
            
        try:
            @database_sync_to_async
            def _delete():
                message = Message.objects.get(
                    id=message_id, 
                    group_id=self.group_id, 
                    sender=self.user
                )
                message.delete()
                
            await _delete()
            
            await self.channel_layer.group_send(
                self.group_name,
                {'type': 'message_deleted', 'message_id': str(message_id)}
            )
            
        except Message.DoesNotExist:
            await self.send_json({'error': 'Cannot delete this message'})

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

    # Group event handlers
    async def chat_message(self, event): 
        await self.send_json({'type': 'chat_message', **event})
    async def reaction_added(self, event): 
        await self.send_json({'type': 'reaction_added', **event})
    async def message_edited(self, event): 
        await self.send_json({'type': 'message_edited', **event})
    async def message_deleted(self, event): 
        await self.send_json({'type': 'message_deleted', **event})
    async def user_typing(self, event): 
        await self.send_json({'type': 'user_typing', **event})
    async def user_stop_typing(self, event): 
        await self.send_json({'type': 'user_stop_typing', **event})
    async def status_update(self, event): 
        await self.send_json({'type': 'status_update', **event})
