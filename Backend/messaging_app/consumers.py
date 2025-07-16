import json
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework_simplejwt.tokens import AccessToken, TokenError
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from messaging_app.models import (
    Message, MessageRequest, GroupChat, Reaction, Attachment
)
from messaging_app.serializers import MessageSerializer
from channels.generic.websocket import AsyncJsonWebsocketConsumer

User = get_user_model()

# ==========================
# ✅ Common helper mixin
# ==========================
class ChatHelperMixin:
    async def get_user_from_token(self):
        """Extract user from token in query string"""
        query_string = self.scope['query_string'].decode()
        token = query_string.split('token=')[1] if 'token=' in query_string else None
        if not token:
            return None
        try:
            user_id = AccessToken(token)['user_id']
            return await database_sync_to_async(User.objects.get)(id=user_id)
        except (TokenError, User.DoesNotExist):
            return None

    async def serialize_message(self, message):
        """Serialize a message for WebSocket broadcast"""
        serializer = MessageSerializer(message, context={'request': None})
        return serializer.data

    async def attach_files(self, message, attachment_ids):
        """Attach files to a message if provided"""
        if attachment_ids:
            attachments = await database_sync_to_async(
                lambda: Attachment.objects.filter(id__in=attachment_ids)
            )()
            await database_sync_to_async(message.attachments.set)(attachments)

    async def broadcast_to_users(self, user_ids, event_type, payload):
        """Send same event to multiple users"""
        for uid in set(user_ids):
            await self.channel_layer.group_send(
                f'user_{uid}',
                {
                    'type': event_type,
                    **payload
                }
            )

# ==========================
# ✅ Private Chat Consumer
# ==========================


class PrivateChatConsumer(ChatHelperMixin, AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = await self.get_user_from_token()
        if not self.user:
            await self.close()
            return
        self.scope['user'] = self.user
        await self.accept()
        await self.send_json({'status': 'connected'})  # ✅ works


    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        actions_map = {
            'send_message': self.send_private_message,
            'add_reaction': self.add_reaction,
            'edit_message': self.edit_message,
            'delete_message': self.delete_message,
            'mark_as_read': self.mark_as_read,
            'typing': self.notify_typing,
            'stop_typing': self.notify_stop_typing
        }

        handler = actions_map.get(action)
        if handler:
            await handler(data)

    async def send_private_message(self, data):
        receiver_id = data.get('receiver_id')
        content = data.get('content')
        attachment_ids = data.get('attachment_ids', [])
        reply_to_id = data.get('reply_to_id')

        try:
            receiver = await database_sync_to_async(User.objects.get)(id=receiver_id)
            sender = self.user

            # ✅ Check existing conversation
            has_conversation = await database_sync_to_async(
                lambda: sender.contacts.filter(id=receiver_id).exists()
                        or Message.objects.filter(sender=sender, receiver=receiver).exists()
                        or Message.objects.filter(sender=receiver, receiver=sender).exists()
            )()

            if not has_conversation:
                # ✅ Create message request instead
                request = await database_sync_to_async(MessageRequest.objects.create)(
                    sender=sender, receiver=receiver, content=content
                )
                await self.send_json({'status': 'pending', 'message': 'Message request sent'})
                await self.broadcast_to_users(
                    [receiver.id], 'message_request', {
                        'message': {
                            'id': str(request.id),
                            'sender': {'id': sender.id, 'first_name': sender.first_name},
                            'content': content,
                            'timestamp': request.timestamp.isoformat()
                        }
                    }
                )
                return

            # ✅ Normal private message
            message = await database_sync_to_async(Message.objects.create)(
                sender=sender, receiver=receiver, content=content, reply_to_id=reply_to_id
            )
            await self.attach_files(message, attachment_ids)
            serialized = await self.serialize_message(message)

            # ✅ Send to sender + receiver
            await self.broadcast_to_users([sender.id, receiver.id], 'chat_message', {'message': serialized})

        except User.DoesNotExist:
            await self.send_json({'error': 'Receiver not found'})

    async def add_reaction(self, data):
        try:
            message = await database_sync_to_async(Message.objects.get)(id=data['message_id'])
            await database_sync_to_async(Reaction.objects.create)(
                message=message, user=self.user, emoji=data['emoji']
            )
            await self.broadcast_to_users(
                [message.sender.id, message.receiver.id],
                'reaction_added',
                {'message_id': str(message.id), 'user_id': str(self.user.id), 'emoji': data['emoji']}
            )
        except Message.DoesNotExist:
            await self.send_json({'error': 'Message not found'})

    async def edit_message(self, data):
        try:
            message = await database_sync_to_async(Message.objects.get)(
                id=data['message_id'], sender=self.user
            )
            message.content = data['new_content']
            await database_sync_to_async(message.save)()
            await self.broadcast_to_users(
                [message.sender.id, message.receiver.id],
                'message_edited',
                {'message_id': str(message.id), 'new_content': data['new_content']}
            )
        except Message.DoesNotExist:
            await self.send_json({'error': 'Cannot edit this message'})

    async def delete_message(self, data):
        try:
            message = await database_sync_to_async(Message.objects.get)(
                id=data['message_id'], sender=self.user
            )
            await database_sync_to_async(message.delete)()
            await self.broadcast_to_users(
                [message.sender.id, message.receiver.id],
                'message_deleted',
                {'message_id': str(message.id)}
            )
        except Message.DoesNotExist:
            await self.send_json({'error': 'Cannot delete this message'})

    async def mark_as_read(self, data):
        receiver_id = data.get('receiver_id')
        await database_sync_to_async(
            lambda: Message.objects.filter(sender_id=receiver_id, receiver=self.user, is_read=False)
                    .update(is_read=True)
        )()
        await self.broadcast_to_users(
            [receiver_id], 'messages_read', {'receiver_id': str(self.user.id)}
        )

    async def notify_typing(self, data):
        await self.broadcast_to_users([data['receiver_id']], 'user_typing', {'user_id': self.user.id})

    async def notify_stop_typing(self, data):
        await self.broadcast_to_users([data['receiver_id']], 'user_stop_typing', {'user_id': self.user.id})

    # ✅ Broadcast handlers
    async def chat_message(self, e): await self.send_json({'type': 'chat_message', **e})
    async def message_request(self, e): await self.send_json({'type': 'message_request', **e})
    async def reaction_added(self, e): await self.send_json({'type': 'reaction_added', **e})
    async def message_edited(self, e): await self.send_json({'type': 'message_edited', **e})
    async def message_deleted(self, e): await self.send_json({'type': 'message_deleted', **e})
    async def messages_read(self, e): await self.send_json({'type': 'messages_read', **e})
    async def user_typing(self, e): await self.send_json({'type': 'user_typing', **e})
    async def user_stop_typing(self, e): await self.send_json({'type': 'user_stop_typing', **e})

# ==========================
# ✅ Group Chat Consumer
# ==========================
class GroupChatConsumer(ChatHelperMixin, AsyncWebsocketConsumer):
    async def connect(self):
        self.group_id = self.scope['url_route']['kwargs']['group_id']
        self.user = await self.get_user_from_token()
        if not self.user:
            return await self.close()

        try:
            group = await database_sync_to_async(GroupChat.objects.get)(id=self.group_id)
            if self.user not in await database_sync_to_async(lambda: list(group.members.all()))():
                return await self.close()

            self.group_name = f'group_{self.group_id}'
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            await self.send_json({'status': 'connected'})

        except GroupChat.DoesNotExist:
            await self.close()

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        actions_map = {
            'send_message': self.send_group_message,
            'add_reaction': self.add_group_reaction,
            'edit_message': self.edit_group_message,
            'delete_message': self.delete_group_message,
            'typing': self.notify_typing,
            'stop_typing': self.notify_stop_typing
        }

        handler = actions_map.get(action)
        if handler:
            await handler(data)

    async def send_group_message(self, data):
        try:
            group = await database_sync_to_async(GroupChat.objects.get)(id=self.group_id)
            message = await database_sync_to_async(Message.objects.create)(
                sender=self.user, group=group,
                content=data.get('content'),
                reply_to_id=data.get('reply_to_id')
            )
            await self.attach_files(message, data.get('attachment_ids', []))
            serialized = await self.serialize_message(message)
            await self.channel_layer.group_send(self.group_name, {'type': 'chat_message', 'message': serialized})
        except GroupChat.DoesNotExist:
            await self.send_json({'error': 'Group not found'})

    async def add_group_reaction(self, data):
        await self._group_message_update(data, 'reaction_added', extra={'emoji': data['emoji']},
                                         action=lambda msg: Reaction.objects.create(
                                             message=msg, user=self.user, emoji=data['emoji']
                                         ))

    async def edit_group_message(self, data):
        await self._group_message_update(data, 'message_edited', extra={'new_content': data['new_content']},
                                         action=lambda msg: setattr(msg, 'content', data['new_content']))

    async def delete_group_message(self, data):
        await self._group_message_update(data, 'message_deleted',
                                         action=lambda msg: msg.delete())

    async def _group_message_update(self, data, event_type, extra=None, action=None):
        """Helper for group message actions"""
        try:
            message = await database_sync_to_async(Message.objects.get)(
                id=data['message_id'], group_id=self.group_id
            )
            if action: await database_sync_to_async(action)(message)
            if hasattr(message, 'save'): await database_sync_to_async(message.save)()
            payload = {'message_id': str(message.id)}
            if extra: payload.update(extra)
            await self.channel_layer.group_send(self.group_name, {'type': event_type, **payload})
        except Message.DoesNotExist:
            await self.send_json({'error': 'Message not found or unauthorized'})

    async def notify_typing(self, _=None):
        await self.channel_layer.group_send(self.group_name, {'type': 'user_typing', 'user_id': self.user.id})

    async def notify_stop_typing(self, _=None):
        await self.channel_layer.group_send(self.group_name, {'type': 'user_stop_typing', 'user_id': self.user.id})

    # ✅ Group broadcast handlers
    async def chat_message(self, e): await self.send_json({'type': 'chat_message', **e})
    async def reaction_added(self, e): await self.send_json({'type': 'reaction_added', **e})
    async def message_edited(self, e): await self.send_json({'type': 'message_edited', **e})
    async def message_deleted(self, e): await self.send_json({'type': 'message_deleted', **e})
    async def user_typing(self, e): await self.send_json({'type': 'user_typing', **e})
    async def user_stop_typing(self, e): await self.send_json({'type': 'user_stop_typing', **e})

# ✅ Utility to avoid repeating json.dumps
    async def send_json(self, data):
        await self.send(text_data=json.dumps(data))
