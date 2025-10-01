from .base import *


class UserMixin:
    """
    Mixin for handling user management events.
    Manages user blocking/unblocking notifications and user-related events.
    """

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