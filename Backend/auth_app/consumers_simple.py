import json
import logging
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger(__name__)

class NotificationConsumer(AsyncWebsocketConsumer):
    """Simplified WebSocket consumer for testing connection stability"""
    
    async def connect(self):
        logger.info(f"WebSocket connect attempt from user: {self.scope['user']}")
        
        # Only allow authenticated users
        if isinstance(self.scope['user'], AnonymousUser):
            logger.warning("WebSocket connection rejected: User not authenticated")
            await self.close(code=4001)
            return
        
        user = self.scope['user']
        logger.info(f"WebSocket connecting authenticated user: {user.username} (ID: {user.id})")
        
        # Accept connection immediately without any blocking operations
        await self.accept()
        logger.info(f"WebSocket connection accepted for user {user.username} (simplified version)")

    async def disconnect(self, close_code):
        if not isinstance(self.scope['user'], AnonymousUser):
            user = self.scope['user']
            logger.info(f"WebSocket disconnecting user {user.username} (ID: {user.id}) with code: {close_code}")
        else:
            logger.info(f"WebSocket disconnected anonymous user with code: {close_code}")

    async def receive(self, text_data):
        logger.debug(f"Received message from user {self.scope['user']}: {text_data}")
        
        # Echo back simple messages for testing
        try:
            data = json.loads(text_data)
            if data.get('type') == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': data.get('timestamp')
                }))
        except (json.JSONDecodeError, Exception) as e:
            logger.debug(f"Error handling received message: {e}")