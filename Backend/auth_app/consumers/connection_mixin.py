from .base import *


class ConnectionMixin:
    """
    Mixin for WebSocket connection lifecycle management.
    Handles connection, disconnection, heartbeat, and basic message receiving.
    """
    
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