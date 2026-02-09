"""
Group chat consumer for multi-user group messaging.
Combines GroupMessageHandlersMixin and MessagingBaseMixin for full functionality.
"""
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from ..models import GroupChat
from .base import MessagingBaseMixin
from .group_handlers import GroupMessageHandlersMixin

logger = logging.getLogger(__name__)


class GroupChatConsumer(GroupMessageHandlersMixin, MessagingBaseMixin, AsyncWebsocketConsumer):
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

    # Group event handlers
    async def chat_message(self, event): 
        """Handle chat message broadcasts."""
        await self.send_json({'type': 'chat_message', **event})
    
    async def reaction_added(self, event): 
        """Handle reaction added events."""
        await self.send_json({'type': 'reaction_added', **event})
    
    async def message_reaction(self, event): 
        """Handle message reaction events for group chats."""
        await self.send_json({'type': 'message_reaction', **event})
    
    async def message_edited(self, event): 
        """Handle message edited broadcasts."""
        await self.send_json({'type': 'message_edited', **event})
    
    async def message_deleted(self, event): 
        """Handle message deleted broadcasts."""
        await self.send_json({'type': 'message_deleted', **event})
    
    async def message_pinned(self, event): 
        """Handle message pinned/unpinned broadcasts."""
        await self.send_json({'type': 'message_pinned', **event})
    
    async def user_typing(self, event): 
        """Handle typing status broadcasts."""
        await self.send_json({'type': 'user_typing', **event})
    
    async def message_read_update(self, event): 
        """Handle message read status updates."""
        await self.send_json({'type': 'message_read_update', **event})
    
    async def user_stop_typing(self, event): 
        """Handle stop typing broadcasts."""
        await self.send_json({'type': 'user_stop_typing', **event})
    
    async def member_request_notification(self, event): 
        """Handle group member request notifications."""
        await self.send_json({'type': 'member_request_notification', **event})
    
    async def group_added_notification(self, event): 
        """Handle group added notifications."""
        await self.send_json({'type': 'group_added_notification', **event})
    
    async def request_response_notification(self, event): 
        """Handle message request response notifications."""
        await self.send_json({'type': 'request_response_notification', **event})
    
    async def group_member_left(self, event): 
        """Handle group member left notifications."""
        await self.send_json({'type': 'group_member_left', **event})
    
    async def group_member_added(self, event): 
        """Handle group member added notifications."""
        await self.send_json({'type': 'group_member_added', **event})
    
    async def group_messages_read(self, event): 
        """Handle group messages read broadcasts."""
        await self.send_json({'type': 'group_messages_read', **event})
    
    async def status_update(self, event): 
        """Handle user status update broadcasts."""
        await self.send_json({'type': 'status_update', **event})
