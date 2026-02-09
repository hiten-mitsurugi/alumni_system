"""
Private chat consumer for one-on-one messaging.
Combines PrivateMessageHandlersMixin and MessagingBaseMixin for full functionality.
"""
import json
import logging
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .base import MessagingBaseMixin
from .private_handlers import PrivateMessageHandlersMixin

logger = logging.getLogger(__name__)


class PrivateChatConsumer(PrivateMessageHandlersMixin, MessagingBaseMixin, AsyncJsonWebsocketConsumer):
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
                'remove_reaction': self.handle_remove_reaction,
                'edit_message': self.handle_edit_message,
                'delete_message': self.handle_delete_message,
                'pin_message': self.handle_pin_message,
                'mark_as_read': self.handle_mark_as_read,
                'typing': self.handle_typing,
                'stop_typing': self.handle_stop_typing,
                'ping': self.handle_ping
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

    # Event handlers for channel layer broadcasts
    async def chat_message(self, event): 
        """Handle incoming chat message broadcasts."""
        await self.send_json({'type': 'chat_message', **event})
    
    async def message_request(self, event): 
        """Handle message request broadcasts."""
        await self.send_json({'type': 'message_request', **event})
    
    async def message_read_update(self, event): 
        """Handle message read status updates."""
        await self.send_json({'type': 'message_read_update', **event})
    
    async def reaction_added(self, event): 
        """Handle reaction added events."""
        await self.send_json({'type': 'reaction_added', **event})
    
    async def message_reaction(self, event): 
        """Handle message reaction events (add/remove/update)."""
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
    
    async def messages_read(self, event): 
        """Handle messages read broadcasts."""
        await self.send_json({'type': 'messages_read', **event})
    
    async def user_typing(self, event): 
        """Handle typing status broadcasts."""
        await self.send_json({'type': 'user_typing', **event})
    
    async def user_stop_typing(self, event): 
        """Handle stop typing broadcasts."""
        await self.send_json({'type': 'user_stop_typing', **event})
    
    async def status_update(self, event): 
        """Handle user status update broadcasts."""
        await self.send_json({'type': 'status_update', **event})
    
    async def notification_update(self, event):
        """Handle notification count updates."""
        await self.send_json({'type': 'notification_update', **event})
    
    async def member_request_notification(self, event): 
        """Handle group member request notifications."""
        await self.send_json({'type': 'member_request_notification', **event})
    
    async def group_added_notification(self, event): 
        """Handle group added notifications."""
        await self.send_json({'type': 'group_added_notification', **event})
    
    async def request_response_notification(self, event): 
        """Handle message request response notifications."""
        await self.send_json({'type': 'request_response_notification', **event})
