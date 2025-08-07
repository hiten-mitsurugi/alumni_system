import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.debug("Attempting WebSocket connection")
        try:
            await self.channel_layer.group_add('admin_notifications', self.channel_name)
            await self.channel_layer.group_add('status_updates', self.channel_name)
            await self.accept()
            logger.debug("WebSocket connection accepted and joined groups 'admin_notifications' and 'status_updates'")
        except Exception as e:
            logger.error(f"WebSocket connect error: {str(e)}")
            await self.close(code=4001)

    async def disconnect(self, close_code):
        logger.debug(f"WebSocket disconnected with code: {close_code}")
        await self.channel_layer.group_discard('admin_notifications', self.channel_name)
        await self.channel_layer.group_discard('status_updates', self.channel_name)

    async def receive(self, text_data):
        logger.debug(f"Received message (usually unused): {text_data}")

    async def notification(self, event):
        # Unified handler for all broadcast notifications
        logger.debug(f"Sending notification: {event['message']}")
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'user': event.get('user', None)  # Optional user info if sent
        }))

    async def status_update(self, event):
        # Handler for user status updates
        logger.info(f"NotificationConsumer: Received status update event: {event}")
        message_data = {
            'type': 'status_update',
            'user_id': event['user_id'],
            'status': event['status'],
            'last_seen': event.get('last_seen')
        }
        logger.info(f"NotificationConsumer: Sending status update message: {message_data}")
        await self.send(text_data=json.dumps(message_data))
