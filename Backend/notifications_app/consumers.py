import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Notification


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time notification delivery.
    Each user has their own notification channel: notifications_user_{user_id}
    """
    
    # ========================================
    # Connection Management
    # ========================================
    
    async def connect(self):
        """
        Accept connection and add to user's notification group.
        Authenticates via JWT token from query string or middleware.
        """
        # Try to get user from scope (if JWT middleware is active)
        self.user = self.scope.get('user')
        
        # If user not in scope or anonymous, try to authenticate via token
        if not self.user or self.user.is_anonymous:
            token = self._get_token_from_query()
            if token:
                self.user = await self._authenticate_user(token)
        
        # Reject if still no valid user
        if not self.user or self.user.is_anonymous:
            await self.close()
            return
        
        # User-specific notification group
        self.notification_group = f'notifications_user_{self.user.id}'
        
        # Join notification group
        await self.channel_layer.group_add(
            self.notification_group,
            self.channel_name
        )
        
        await self.accept()
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': f'Connected to notifications for user {self.user.id}'
        }))
        
        print(f"✅ Notification WebSocket connected for user: {self.user.email}")
    
    async def disconnect(self, close_code):
        """Remove from notification group on disconnect."""
        if hasattr(self, 'notification_group'):
            await self.channel_layer.group_discard(
                self.notification_group,
                self.channel_name
            )
            if hasattr(self, 'user'):
                print(f"🔌 Notification WebSocket disconnected for user: {self.user.email}")
    
    # ========================================
    # Message Handlers
    # ========================================
    
    async def receive(self, text_data):
        """
        Handle messages from WebSocket client.
        Supports marking notifications as read.
        """
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'mark_as_read':
                await self._handle_mark_as_read(data)
            else:
                await self._send_error(f'Unknown action: {action}')
                
        except json.JSONDecodeError:
            await self._send_error('Invalid JSON')
        except Exception as e:
            await self._send_error(f'Error: {str(e)}')
    
    async def notification_message(self, event):
        """
        Handler for notification.message events sent to the group.
        Broadcasts notification to the connected user.
        """
        notification_data = event['notification']
        
        # Send notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': notification_data
        }))
        
        print(f"📡 Sent notification to user {self.user.id}: {notification_data.get('title')}")
    
    # ========================================
    # Helper Methods
    # ========================================
    
    def _get_token_from_query(self):
        """Extract JWT token from query string."""
        query_string = self.scope.get('query_string', b'').decode()
        if not query_string:
            return None
        
        try:
            params = dict(param.split('=') for param in query_string.split('&') if '=' in param)
            return params.get('token')
        except Exception:
            return None
    
    @database_sync_to_async
    def _authenticate_user(self, token):
        """Authenticate user via JWT token."""
        try:
            from auth_app.middleware import get_user_from_token
            return get_user_from_token(token)
        except Exception as e:
            print(f"❌ Token authentication failed: {e}")
            return None
    
    async def _send_error(self, message):
        """Send error message to client."""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message
        }))
    
    async def _handle_mark_as_read(self, data):
        """Handle mark-as-read action from client."""
        notification_id = data.get('notification_id')
        
        if not notification_id:
            await self._send_error('notification_id required')
            return
        
        success = await self._mark_notification_as_read(notification_id)
        
        if success:
            await self.send(text_data=json.dumps({
                'type': 'mark_as_read_success',
                'notification_id': notification_id
            }))
        else:
            await self._send_error(f'Failed to mark notification {notification_id} as read')
    
    @database_sync_to_async
    def _mark_notification_as_read(self, notification_id):
        """Mark notification as read in database (async wrapper)."""
        try:
            notification = Notification.objects.get(
                id=notification_id,
                user=self.user
            )
            notification.mark_as_read()
            return True
        except Notification.DoesNotExist:
            print(f"⚠️ Notification {notification_id} not found for user {self.user.id}")
            return False
        except Exception as e:
            print(f"⚠️ Error marking notification as read: {e}")
            return False

