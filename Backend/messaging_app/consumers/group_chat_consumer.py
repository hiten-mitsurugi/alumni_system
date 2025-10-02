"""
Clean, well-documented WebSocket consumer for group messaging.
Uses mixin classes for handler organization.
"""

import json
import logging
from typing import Dict, Any
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from messaging_app.models import GroupChat
from .base_mixin import MessagingBaseMixin
from .group_message_handlers import GroupMessageHandlersMixin
from .group_reaction_handlers import GroupReactionHandlersMixin
from .group_edit_handlers import GroupEditHandlersMixin
from .group_utility_handlers import GroupUtilityHandlersMixin

logger = logging.getLogger(__name__)


class GroupChatConsumer(
    MessagingBaseMixin,
    GroupMessageHandlersMixin,
    GroupReactionHandlersMixin,
    GroupEditHandlersMixin,
    GroupUtilityHandlersMixin,
    AsyncWebsocketConsumer
):
    """
    WebSocket consumer for group messaging.
    Handles group message sending, reactions, editing, and deletion.
    
    Handler methods are organized in separate mixin classes:
    - GroupMessageHandlersMixin: send_message, bump_message
    - GroupReactionHandlersMixin: add_reaction, remove_reaction
    - GroupEditHandlersMixin: edit_message, delete_message
    - GroupUtilityHandlersMixin: pin_message, typing, mark_as_read
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
                'remove_reaction': self.handle_group_remove_reaction,
                'edit_message': self.handle_group_edit,
                'delete_message': self.handle_group_delete,
                'pin_message': self.handle_group_pin,
                'typing': self.handle_group_typing,
                'stop_typing': self.handle_group_stop_typing,
                'mark_as_read': self.handle_group_mark_as_read,
                'ping': self.handle_ping
            }
            
            handler = handlers.get(action)
            if handler:
                await handler(data)
            else:
                await self.send_json({'error': f'Unknown action: {action}'})
                
        except json.JSONDecodeError:
            await self.send_json({'error': 'Invalid JSON'})

    async def send_json(self, data: Dict[str, Any]) -> None:
        """Send JSON data to client."""
        await self.send(text_data=json.dumps(data))

    # Group event handlers
    async def chat_message(self, event): 
        await self.send_json({'type': 'chat_message', **event})
    async def reaction_added(self, event): 
        await self.send_json({'type': 'reaction_added', **event})
    async def message_reaction(self, event): 
        await self.send_json({'type': 'message_reaction', **event})
    async def message_edited(self, event): 
        await self.send_json({'type': 'message_edited', **event})
    async def message_deleted(self, event): 
        await self.send_json({'type': 'message_deleted', **event})
    async def message_pinned(self, event): 
        await self.send_json({'type': 'message_pinned', **event})
    async def user_typing(self, event): 
        await self.send_json({'type': 'user_typing', **event})
    async def message_read_update(self, event): 
        await self.send_json({'type': 'message_read_update', **event})
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
    async def group_messages_read(self, event): 
        await self.send_json({'type': 'group_messages_read', **event})
    async def status_update(self, event): 
        await self.send_json({'type': 'status_update', **event})
