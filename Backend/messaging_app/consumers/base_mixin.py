"""
Clean, well-documented WebSocket consumers for messaging functionality.
Handles private messages and group chats with reply threading support.
"""

import json
import logging
import re
from typing import Optional, List, Dict, Any
from channels.generic.websocket import AsyncWebsocketConsumer, AsyncJsonWebsocketConsumer
from rest_framework_simplejwt.tokens import AccessToken, TokenError
from django.contrib.auth import get_user_model
from django.db.models import Q
from channels.db import database_sync_to_async
from django.utils import timezone
from django.core.cache import cache

from messaging_app.models import Message, MessageRequest, GroupChat, MessageReaction, Attachment, MessageRead, MessageMention
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
            # Use dynamic host for media URLs
            import os
            host = os.environ.get('SERVER_HOST')
            if not host:
                # Try to get from ASGI scope headers if available
                try:
                    host = dict(self.scope.get('headers', [])).get(b'host', b'').decode() or 'localhost:8000'
                except Exception:
                    host = 'localhost:8000'
            scheme = 'https' if os.environ.get('SERVER_HTTPS', '0') == '1' else 'http'
            mock_request.META = {'HTTP_HOST': host, 'wsgi.url_scheme': scheme}
            
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
