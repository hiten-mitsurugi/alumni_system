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
from django.core.cache import cache

from messaging_app.models import Message, MessageRequest, GroupChat, Reaction, Attachment
from messaging_app.serializers import MessageSerializer

logger = logging.getLogger(__name__)
User = get_user_model()

# Track active connections per user
ACTIVE_CONNECTIONS = {}


class MessagingBaseMixin:
    """
    Base mixin providing common functionality for all messaging consumers.
    Handles authentication, user status updates, and message serialization.
    """
    
    async def authenticate_user(self):
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

    async def update_user_status(self, user, status: str) -> None:
        """Update user's online status and last seen timestamp with connection tracking."""
        @database_sync_to_async
        def _update_status():
            try:
                from django.utils import timezone as tz
                from auth_app.models import Profile
                profile, created = Profile.objects.get_or_create(user=user)
                
                old_status = profile.status
                
                if status == 'online':
                    profile.status = 'online'
                    profile.last_seen = tz.now()
                elif status == 'activity':
                    # Keep current status, just update last_seen (don't change online status)
                    profile.last_seen = tz.now()
                    # Don't change status from online to anything else unless explicitly set to offline
                    
                profile.save()
                
                # Return both old and new status for broadcasting
                return old_status, profile.status
                
            except Exception as e:
                logger.error(f"Error updating user status: {e}")
                return None, None
                
        old_status, new_status = await _update_status()
        
        # Broadcast status change if it actually changed to online
        if old_status != new_status and new_status == 'online':
            from django.utils import timezone as tz
            await self.channel_layer.group_send(
                'status_updates',
                {
                    'type': 'status_update',
                    'user_id': user.id,
                    'status': new_status,
                    'last_seen': tz.now().isoformat()
                }
            )

    def add_user_connection(self, user_id: int, channel_name: str):
        """Track a new connection for a user."""
        if user_id not in ACTIVE_CONNECTIONS:
            ACTIVE_CONNECTIONS[user_id] = set()
        ACTIVE_CONNECTIONS[user_id].add(channel_name)
        logger.debug(f"Added connection for user {user_id}. Total connections: {len(ACTIVE_CONNECTIONS[user_id])}")

    def remove_user_connection(self, user_id: int, channel_name: str):
        """Remove a connection for a user and return True if it was the last connection."""
        if user_id in ACTIVE_CONNECTIONS:
            ACTIVE_CONNECTIONS[user_id].discard(channel_name)
            if not ACTIVE_CONNECTIONS[user_id]:  # No more connections
                del ACTIVE_CONNECTIONS[user_id]
                logger.debug(f"Removed last connection for user {user_id}")
                return True
            logger.debug(f"Removed connection for user {user_id}. Remaining connections: {len(ACTIVE_CONNECTIONS[user_id])}")
        return False

    async def set_user_offline(self, user):
        """Set user offline and broadcast the status change."""
        @database_sync_to_async
        def _set_offline():
            try:
                from django.utils import timezone as tz
                from auth_app.models import Profile
                profile, created = Profile.objects.get_or_create(user=user)
                profile.status = 'offline'
                profile.last_seen = tz.now()
                profile.save()
                return True
            except Exception as e:
                logger.error(f"Error setting user offline: {e}")
                return False
                
        if await _set_offline():
            from django.utils import timezone as tz
            await self.channel_layer.group_send(
                'status_updates',
                {
                    'type': 'status_update',
                    'user_id': user.id,
                    'status': 'offline',
                    'last_seen': tz.now().isoformat()
                }
            )

    async def _is_user_blocked(self, blocker, blocked_user) -> bool:
        """Check if blocker has blocked blocked_user."""
        @database_sync_to_async
        def _check_blocked():
            from messaging_app.models import BlockedUser
            return BlockedUser.objects.filter(
                user=blocker,
                blocked_user=blocked_user
            ).exists()
        
        return await _check_blocked()

    async def serialize_message(self, message: Message) -> Dict[str, Any]:
        """Serialize message for WebSocket transmission with proper UUID handling."""
        @database_sync_to_async
        def _serialize():
            # Create mock request for URL building with user context
            from django.http import HttpRequest
            mock_request = HttpRequest()
            mock_request.META = {'HTTP_HOST': '127.0.0.1:8000', 'wsgi.url_scheme': 'http'}
            
            # Create a proper user object with is_authenticated attribute
            mock_user = self.user
            if hasattr(mock_user, 'is_authenticated'):
                # User already has is_authenticated, use as-is
                mock_request.user = mock_user
            else:
                # Create a wrapper to add is_authenticated
                class MockAuthenticatedUser:
                    def __init__(self, user):
                        self._user = user
                        self.is_authenticated = True
                        
                    def __getattr__(self, name):
                        return getattr(self._user, name)
                        
                    @property
                    def id(self):
                        return self._user.id
                        
                    @property  
                    def username(self):
                        return self._user.username
                
                mock_request.user = MockAuthenticatedUser(mock_user)
            
            serializer = MessageSerializer(message, context={'request': mock_request})
            data = serializer.data
            
            # ✅ FIX: Convert ALL UUIDs to strings for WebSocket serialization
            def convert_uuids_to_strings(obj):
                """Recursively convert UUID objects to strings in nested dictionaries."""
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if hasattr(value, 'hex'):  # UUID objects have a 'hex' attribute
                            obj[key] = str(value)
                        elif isinstance(value, dict):
                            convert_uuids_to_strings(value)
                        elif isinstance(value, list):
                            for item in value:
                                if isinstance(item, dict):
                                    convert_uuids_to_strings(item)
                                elif hasattr(item, 'hex'):
                                    # This shouldn't happen in our data structure, but just in case
                                    pass
                elif isinstance(obj, list):
                    for item in obj:
                        if isinstance(item, dict):
                            convert_uuids_to_strings(item)
            
            # Convert all UUIDs in the serialized data
            convert_uuids_to_strings(data)
                
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
            
        # Track this connection
        self.add_user_connection(self.user.id, self.channel_name)
        
        # Set user online and join personal channel
        await self.update_user_status(self.user, 'online')
        self.user_group = f'user_{self.user.id}'
        await self.channel_layer.group_add(self.user_group, self.channel_name)
        await self.channel_layer.group_add('status_updates', self.channel_name)
        
        await self.accept()
        await self.send_json({'status': 'connected'})
        logger.info(f"User {self.user.id} connected to private chat")

    async def disconnect(self, close_code):
        """Clean up on disconnect - only set offline if last connection."""
        if hasattr(self, 'user') and self.user:
            # Check if this was the user's last connection
            is_last_connection = self.remove_user_connection(self.user.id, self.channel_name)
            
            if is_last_connection:
                # Only set offline if this was the last connection
                await self.set_user_offline(self.user)
            else:
                # Just update activity timestamp
                await self.update_user_status(self.user, 'activity')
            
        # Leave groups
        if hasattr(self, 'user_group'):
            await self.channel_layer.group_discard(self.user_group, self.channel_name)
        await self.channel_layer.group_discard('status_updates', self.channel_name)
        
        user_id = getattr(self.user, 'id', 'unknown') if hasattr(self, 'user') and self.user else 'unknown'
        logger.info(f"User {user_id} disconnected")

    async def receive(self, text_data):
        """Route incoming messages to appropriate handlers."""
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            # Action routing map
            handlers = {
                'send_message': self.handle_send_message,
                'bump_message': self.handle_bump_message,
                'add_reaction': self.handle_add_reaction,
                'edit_message': self.handle_edit_message,
                'delete_message': self.handle_delete_message,
                'pin_message': self.handle_pin_message,
                'mark_as_read': self.handle_mark_as_read,
                'typing': self.handle_typing,
                'stop_typing': self.handle_stop_typing,
                'ping': self.handle_ping  # Add ping handler
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

    async def handle_ping(self, data: Dict[str, Any]):
        """Handle ping messages to keep connection alive."""
        await self.update_user_status(self.user, 'activity')
        from django.utils import timezone as tz
        await self.send_json({'action': 'pong', 'timestamp': tz.now().isoformat()})

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
        
        logger.info(f"Edit request: message_id={message_id}, new_content='{new_content}', user={self.user.id}")
        
        if not message_id or not new_content:
            logger.warning(f"Edit validation failed: message_id={message_id}, new_content='{new_content}'")
            return await self.send_json({'error': 'message_id and new_content are required'})
            
        try:
            @database_sync_to_async
            def _edit():
                from django.utils import timezone as tz
                logger.info(f"Looking for message with id={message_id} and sender={self.user.id}")
                message = Message.objects.get(id=message_id, sender=self.user)
                logger.info(f"Found message: {message.id}, current content: '{message.content}'")
                message.content = new_content
                message.edited_at = tz.now()  # Set edit timestamp
                message.save()
                logger.info(f"Message saved successfully with new content: '{message.content}'")
                
                # Get user IDs for broadcasting - must be done in sync context
                users = [message.sender.id, message.receiver.id] if message.receiver else [message.sender.id]
                return message, message.edited_at, users
                
            message, edited_at, users = await _edit()
            
            # Broadcast to participants
            logger.info(f"Broadcasting edit to users: {users}")
            await self.broadcast_to_users(
                users,
                'message_edited',
                {
                    'message_id': str(message.id), 
                    'new_content': new_content,
                    'edited_at': edited_at.isoformat()
                }
            )
            
            # Send success confirmation to sender
            await self.send_json({
                'status': 'success', 
                'action': 'message_edited',
                'message_id': str(message.id)
            })
            logger.info(f"Edit completed successfully for message {message.id}")
            
        except Message.DoesNotExist:
            logger.error(f"Message not found: id={message_id}, sender={self.user.id}")
            await self.send_json({'error': 'Cannot edit this message'})
        except Exception as e:
            logger.error(f"Error editing message {message_id}: {e}", exc_info=True)
            await self.send_json({'error': 'Failed to edit message'})

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
            
            # Send success confirmation to sender
            await self.send_json({
                'status': 'success', 
                'action': 'message_deleted',
                'message_id': str(message_id)
            })
            
        except Message.DoesNotExist:
            await self.send_json({'error': 'Cannot delete this message'})

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
    async def message_pinned(self, event): 
        await self.send_json({'type': 'message_pinned', **event})
    async def messages_read(self, event): 
        await self.send_json({'type': 'messages_read', **event})
    async def user_typing(self, event): 
        await self.send_json({'type': 'user_typing', **event})
    async def user_stop_typing(self, event): 
        await self.send_json({'type': 'user_stop_typing', **event})
    async def status_update(self, event): 
        await self.send_json({'type': 'status_update', **event})
    async def member_request_notification(self, event): 
        await self.send_json({'type': 'member_request_notification', **event})
    async def group_added_notification(self, event): 
        await self.send_json({'type': 'group_added_notification', **event})
    async def request_response_notification(self, event): 
        await self.send_json({'type': 'request_response_notification', **event})


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
                
            # Track this connection
            self.add_user_connection(self.user.id, self.channel_name)
                
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
        """Clean up on disconnect - only set offline if last connection."""
        if hasattr(self, 'user') and self.user:
            # Check if this was the user's last connection
            is_last_connection = self.remove_user_connection(self.user.id, self.channel_name)
            
            if is_last_connection:
                # Only set offline if this was the last connection
                await self.set_user_offline(self.user)
            else:
                # Just update activity timestamp
                await self.update_user_status(self.user, 'activity')
            
        # Leave groups
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.channel_layer.group_discard('status_updates', self.channel_name)
        
        user_id = getattr(self.user, 'id', 'unknown') if hasattr(self, 'user') and self.user else 'unknown'
        logger.info(f"User {user_id} left group")

    async def receive(self, text_data):
        """Route group message actions."""
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            handlers = {
                'send_message': self.handle_group_message,
                'bump_message': self.handle_group_bump,
                'add_reaction': self.handle_group_reaction,
                'edit_message': self.handle_group_edit,
                'delete_message': self.handle_group_delete,
                'pin_message': self.handle_group_pin,
                'typing': self.handle_group_typing,
                'stop_typing': self.handle_group_stop_typing,
                'ping': self.handle_ping  # Add ping handler
            }
            
            handler = handlers.get(action)
            if handler:
                await handler(data)
            else:
                await self.send_json({'error': f'Unknown action: {action}'})
                
        except json.JSONDecodeError:
            await self.send_json({'error': 'Invalid JSON'})

    async def handle_ping(self, data: Dict[str, Any]):
        """Handle ping messages to keep connection alive."""
        await self.update_user_status(self.user, 'activity')
        from django.utils import timezone as tz
        await self.send_json({'action': 'pong', 'timestamp': tz.now().isoformat()})

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
                from django.utils import timezone as tz
                message = Message.objects.get(
                    id=message_id, 
                    group_id=self.group_id, 
                    sender=self.user
                )
                message.content = new_content
                message.edited_at = tz.now()  # Set edit timestamp
                message.save()
                return message.edited_at
                
            edited_at = await _edit()
            
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'message_edited',
                    'message_id': str(message_id),
                    'new_content': new_content,
                    'edited_at': edited_at.isoformat()
                }
            )
            
            # Send success confirmation to sender
            await self.send_json({
                'status': 'success', 
                'action': 'message_edited',
                'message_id': str(message_id)
            })
            
        except Message.DoesNotExist:
            await self.send_json({'error': 'Cannot edit this message'})
        except Exception as e:
            logger.error(f"Error editing group message: {e}")
            await self.send_json({'error': 'Failed to edit message'})

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
            
            # Send success confirmation to sender
            await self.send_json({
                'status': 'success', 
                'action': 'message_deleted',
                'message_id': str(message_id)
            })
            
        except Message.DoesNotExist:
            await self.send_json({'error': 'Cannot delete this message'})

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

    # Group event handlers
    async def chat_message(self, event): 
        await self.send_json({'type': 'chat_message', **event})
    async def reaction_added(self, event): 
        await self.send_json({'type': 'reaction_added', **event})
    async def message_edited(self, event): 
        await self.send_json({'type': 'message_edited', **event})
    async def message_deleted(self, event): 
        await self.send_json({'type': 'message_deleted', **event})
    async def message_pinned(self, event): 
        await self.send_json({'type': 'message_pinned', **event})
    async def user_typing(self, event): 
        await self.send_json({'type': 'user_typing', **event})
    async def user_stop_typing(self, event): 
        await self.send_json({'type': 'user_stop_typing', **event})
    async def member_request_notification(self, event): 
        await self.send_json({'type': 'member_request_notification', **event})
    async def group_added_notification(self, event): 
        await self.send_json({'type': 'group_added_notification', **event})
    async def request_response_notification(self, event): 
        await self.send_json({'type': 'request_response_notification', **event})
    async def group_member_left(self, event): 
        await self.send_json({'type': 'group_member_left', **event})
    async def group_member_added(self, event): 
        await self.send_json({'type': 'group_member_added', **event})
    async def status_update(self, event): 
        await self.send_json({'type': 'status_update', **event})
