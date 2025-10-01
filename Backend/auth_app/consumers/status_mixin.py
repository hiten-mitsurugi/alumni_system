from .base import *


class StatusMixin:
    """
    Mixin for handling user status updates (online/offline).
    Manages status broadcasts and real-time status changes.
    """

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