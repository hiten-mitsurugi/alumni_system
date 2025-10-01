from .base import *


class MessageMixin:
    """
    Mixin for handling message-related notifications and events.
    Manages message read receipts and message-related broadcasts.
    """

    async def messages_read(self, event):
        logger.info(f"NotificationConsumer: Sending messages_read event to user {self.scope['user']}")
        await self.send(text_data=json.dumps({
            'type': 'messages_read',
            'message': event.get('message', 'Messages marked as read'),
            'conversation_id': event.get('conversation_id'),
            'user_id': event.get('user_id')
        }))