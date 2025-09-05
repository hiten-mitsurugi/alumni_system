import json
import logging
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from .status_cache import UserStatusCache

logger = logging.getLogger(__name__)

class NotificationConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.heartbeat_task = None
        self.heartbeat_interval = 30  # Send heartbeat every 30 seconds
    
    async def connect(self):
        logger.info(f"WebSocket connect attempt from user: {self.scope['user']}")
        
        # Only allow authenticated users
        if isinstance(self.scope['user'], AnonymousUser):
            logger.warning("WebSocket connection rejected: User not authenticated")
            await self.close(code=4001)
            return
        
        try:
            user = self.scope['user']
            logger.info(f"WebSocket connecting authenticated user: {user.username} (ID: {user.id})")
            
            # Set user online when WebSocket connects (for real-time status)
            await database_sync_to_async(UserStatusCache.set_user_online)(user.id)
            logger.info(f"Set user {user.id} online via WebSocket connect")
            
            # Join global groups
            await self.channel_layer.group_add('admin_notifications', self.channel_name)
            await self.channel_layer.group_add('status_updates', self.channel_name)
            await self.channel_layer.group_add('user_management', self.channel_name)
            
            # Join user-specific group for personal notifications
            await self.channel_layer.group_add(f'user_{user.id}', self.channel_name)
            
            await self.accept()
            
            # Start heartbeat to keep user online
            self.heartbeat_task = asyncio.create_task(self.heartbeat_loop())
            
            logger.info(f"WebSocket connection accepted for user {user.username} with heartbeat")
            
        except Exception as e:
            logger.error(f"WebSocket connect error for user {self.scope['user']}: {str(e)}")
            await self.close(code=4001)

    async def disconnect(self, close_code):
        if not isinstance(self.scope['user'], AnonymousUser):
            user = self.scope['user']
            logger.info(f"WebSocket disconnecting user {user.username} (ID: {user.id}) with code: {close_code}")
            
            # Cancel heartbeat task
            if self.heartbeat_task:
                self.heartbeat_task.cancel()
                
            # Set user offline when WebSocket disconnects (for real-time status)
            try:
                await database_sync_to_async(UserStatusCache.set_user_offline)(user.id)
                logger.info(f"Set user {user.id} offline via WebSocket disconnect")
            except Exception as e:
                logger.error(f"Error setting user {user.id} offline: {e}")
            
            # Leave all groups
            await self.channel_layer.group_discard('admin_notifications', self.channel_name)
            await self.channel_layer.group_discard('status_updates', self.channel_name)
            await self.channel_layer.group_discard('user_management', self.channel_name)
            await self.channel_layer.group_discard(f'user_{user.id}', self.channel_name)
        else:
            logger.info(f"WebSocket disconnected anonymous user with code: {close_code}")
    
    async def heartbeat_loop(self):
        """Send periodic heartbeat to keep user status fresh"""
        try:
            while True:
                await asyncio.sleep(self.heartbeat_interval)
                if not isinstance(self.scope['user'], AnonymousUser):
                    user = self.scope['user']
                    # Refresh user activity to keep them online
                    await database_sync_to_async(UserStatusCache.set_user_online)(user.id)
                    logger.debug(f"Heartbeat: refreshed online status for user {user.id}")
        except asyncio.CancelledError:
            logger.debug("Heartbeat cancelled")
        except Exception as e:
            logger.error(f"Heartbeat error: {e}")

    async def receive(self, text_data):
        logger.debug(f"Received message from user {self.scope['user']}: {text_data}")
        
        # Handle heartbeat responses from frontend
        try:
            data = json.loads(text_data)
            if data.get('type') == 'heartbeat':
                if not isinstance(self.scope['user'], AnonymousUser):
                    user = self.scope['user']
                    # Refresh user status on heartbeat
                    await database_sync_to_async(UserStatusCache.set_user_online)(user.id)
                    await self.send(text_data=json.dumps({
                        'type': 'heartbeat_ack',
                        'timestamp': data.get('timestamp')
                    }))
        except (json.JSONDecodeError, Exception) as e:
            logger.debug(f"Error handling received message: {e}")

    async def notification(self, event):
        # Unified handler for all broadcast notifications
        logger.debug(f"Sending notification to user {self.scope['user']}: {event['message']}")
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'user': event.get('user', None)  # Optional user info if sent
        }))

    async def status_update(self, event):
        # Handler for user status updates
        user = self.scope['user']
        logger.info(f"NotificationConsumer: Sending status update to user {user.username}: {event}")
        
        # Handle different event structures
        if 'data' in event:
            # New structure: {'type': 'status_update', 'data': {...}}
            data = event['data']
            message_data = {
                'type': 'status_update',
                'data': {
                    'user_id': data['user_id'],
                    'status': data['status'],
                    'timestamp': data.get('timestamp')
                }
            }
        else:
            # Legacy structure: {'type': 'status_update', 'user_id': ..., 'status': ...}
            message_data = {
                'type': 'status_update',
                'data': {
                    'user_id': event['user_id'],
                    'status': event['status'],
                    'timestamp': event.get('timestamp', event.get('last_seen'))
                }
            }
        
        logger.info(f"NotificationConsumer: Broadcasting status update to user {user.username}: {message_data}")
        await self.send(text_data=json.dumps(message_data))

    # Handler for blocking/unblocking events
    async def user_blocked(self, event):
        logger.info(f"NotificationConsumer: Sending user_blocked event to user {self.scope['user']}")
        await self.send(text_data=json.dumps({
            'type': 'user_blocked',
            'message': event['message'],
            'blocked_by': event['blocked_by']
        }))

    async def user_unblocked(self, event):
        logger.info(f"NotificationConsumer: Sending user_unblocked event to user {self.scope['user']}")
        await self.send(text_data=json.dumps({
            'type': 'user_unblocked',
            'message': event['message'],
            'unblocked_by': event['unblocked_by']
        }))

    # Handler for group creation notifications
    async def group_created(self, event):
        logger.info(f"NotificationConsumer: Sending group_created event to user {self.scope['user']}")
        await self.send(text_data=json.dumps({
            'type': 'group_created',
            'group': event['group'],
            'creator': event['creator']
        }))

    # Handler for messages read notifications
    async def messages_read(self, event):
        logger.info(f"NotificationConsumer: Sending messages_read event to user {self.scope['user']}")
        await self.send(text_data=json.dumps({
            'type': 'messages_read',
            'message': event.get('message', 'Messages marked as read'),
            'conversation_id': event.get('conversation_id'),
            'user_id': event.get('user_id')
        }))

    # Handler for group member added notifications
    async def group_member_added(self, event):
        logger.info(f"NotificationConsumer: Sending group_member_added event to user {self.scope['user']}")
        await self.send(text_data=json.dumps({
            'type': 'group_member_added',
            'group_id': event.get('group_id'),
            'group_name': event.get('group_name'),
            'added_user': event.get('added_user', {}),
            'added_by': event.get('added_by', {}),
            'system_message': event.get('system_message', {})
        }))

    # Handler for group member left notifications
    async def group_member_left(self, event):
        logger.info(f"NotificationConsumer: Sending group_member_left event to user {self.scope['user']}")
        await self.send(text_data=json.dumps({
            'type': 'group_member_left',
            'group_id': event.get('group_id'),
            'group_name': event.get('group_name'),
            'removed_by': event.get('removed_by', {})
        }))

    # Handler for broadcasting messages to user management group
    async def broadcast_message(self, event):
        logger.info(f"NotificationConsumer: Broadcasting message to user {self.scope['user']}")
        await self.send(text_data=json.dumps(event.get('message', {})))
 
    # Handler for notification updates (for messaging badge counts)
    async def notification_update(self, event):
        logger.info(f"NotificationConsumer: Sending notification_update to user {self.scope['user']}")
        await self.send(text_data=json.dumps({
            'type': 'notification_update',
            'data': event.get('data', {})
        }))

    # Handler for group message preview (unread counters/highlight)
    async def group_message_preview(self, event):
        logger.info(f"NotificationConsumer: Sending group_message_preview to user {self.scope['user']}")
        await self.send(text_data=json.dumps({
            'type': 'group_message_preview',
            'message': event.get('message', {})
        }))

    # 🔔 MENTIONS: Handler for mention notifications
    async def mention_notification(self, event):
        logger.info(f"NotificationConsumer: Sending mention notification to user {self.scope['user']}")
        await self.send(text_data=json.dumps({
            'type': 'mention_notification',
            'data': event['data']
        }))
