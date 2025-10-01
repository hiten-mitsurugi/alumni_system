from .base import *


class GroupMixin:
    """
    Mixin for handling group-related events and notifications.
    Manages group creation, member additions/removals, and group message previews.
    """

    async def group_created(self, event):
        logger.info(f"NotificationConsumer: Sending group_created event to user {self.scope['user']}")
        await self.send(text_data=json.dumps({
            'type': 'group_created',
            'group': event['group'],
            'creator': event['creator']
        }))

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

    async def group_member_left(self, event):
        logger.info(f"NotificationConsumer: Sending group_member_left event to user {self.scope['user']}")
        await self.send(text_data=json.dumps({
            'type': 'group_member_left',
            'group_id': event.get('group_id'),
            'group_name': event.get('group_name'),
            'removed_by': event.get('removed_by', {})
        }))

    async def group_message_preview(self, event):
        logger.info(f"NotificationConsumer: Sending group_message_preview to user {self.scope['user']}")
        await self.send(text_data=json.dumps({
            'type': 'group_message_preview',
            'message': event.get('message', {})
        }))