from .base import *


class NotificationMixin:
    """
    Mixin for handling general notifications, updates, and broadcasts.
    Manages notification updates, mentions, and broadcast messages.
    """

    async def notification(self, event):
        # Unified handler for all broadcast notifications
        logger.debug(f"Sending notification to user {self.scope['user']}: {event['message']}")
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'user': event.get('user', None)  # Optional user info if sent
        }))

    async def broadcast_message(self, event):
        logger.info(f"NotificationConsumer: Broadcasting message to user {self.scope['user']}")
        await self.send(text_data=json.dumps(event.get('message', {})))
 
    async def notification_update(self, event):
        logger.info(f"NotificationConsumer: Sending notification_update to user {self.scope['user']}")
        await self.send(text_data=json.dumps({
            'type': 'notification_update',
            'data': event.get('data', {})
        }))

    async def mention_notification(self, event):
        logger.info(f"NotificationConsumer: Sending mention notification to user {self.scope['user']}")
        await self.send(text_data=json.dumps({
            'type': 'mention_notification',
            'data': event['data']
        }))