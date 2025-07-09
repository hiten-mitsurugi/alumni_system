import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message, GroupChat, Reaction, Attachment
from django.core.files.base import ContentFile
import base64
from django.core.cache import cache

class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return
        self.room_name = f"private_{self.user.id}"
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        if action == 'send_message':
            await self.send_private_message(data)
        elif action == 'react':
            await self.add_reaction(data)
        elif action == 'delete':
            await self.delete_message(data)

    async def send_private_message(self, data):
        receiver_id = data['receiver_id']
        content = data['content']
        receiver = await database_sync_to_async(User.objects.get)(id=receiver_id)
        message = await database_sync_to_async(Message.objects.create)(
            sender=self.user,
            receiver=receiver,
            content=content
        )
        if 'attachments' in data:
            for attachment in data['attachments']:
                file_data = base64.b64decode(attachment['data'])
                file = ContentFile(file_data, name=attachment['name'])
                await database_sync_to_async(Attachment.objects.create)(
                    message=message,
                    file=file,
                    file_type=attachment['type']
                )
        await self.channel_layer.group_send(
            f"private_{receiver_id}",
            {
                'type': 'chat_message',
                'message': {
                    'id': message.id,
                    'sender': self.user.username,
                    'content': content,
                    'timestamp': message.timestamp.isoformat(),
                }
            }
        )
        await self.send(text_data=json.dumps({
            'status': 'message_sent',
            'message_id': message.id
        }))
        cache.delete(f"messages_private_{self.user.id}_{receiver_id}")

    async def add_reaction(self, data):
        message_id = data['message_id']
        reaction_type = data['reaction_type']
        message = await database_sync_to_async(Message.objects.get)(id=message_id)
        await database_sync_to_async(Reaction.objects.get_or_create)(
            message=message,
            user=self.user,
            reaction_type=reaction_type
        )
        target = f"private_{message.receiver.id}" if message.receiver else f"group_{message.group.id}"
        await self.channel_layer.group_send(
            target,
            {
                'type': 'reaction_added',
                'message_id': message_id,
                'reaction': reaction_type,
                'user': self.user.username
            }
        )

    async def delete_message(self, data):
        message_id = data['message_id']
        message = await database_sync_to_async(Message.objects.get)(id=message_id, sender=self.user)
        await database_sync_to_async(message.delete)()
        target = f"private_{message.receiver.id}" if message.receiver else f"group_{message.group.id}"
        await self.channel_layer.group_send(
            target,
            {
                'type': 'message_deleted',
                'message_id': message_id
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event['message']))

    async def reaction_added(self, event):
        await self.send(text_data=json.dumps(event))

    async def message_deleted(self, event):
        await self.send(text_data=json.dumps(event))

class GroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return
        self.group_id = self.scope['url_route']['kwargs']['group_id']
        self.group = await database_sync_to_async(GroupChat.objects.get)(id=self.group_id)
        if self.user not in await database_sync_to_async(self.group.members.all)():
            await self.close()
            return
        self.room_name = f"group_{self.group_id}"
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        if action == 'send_message':
            await self.send_group_message(data)
        elif action == 'react':
            await self.add_reaction(data)
        elif action == 'delete':
            await self.delete_message(data)

    async def send_group_message(self, data):
        content = data['content']
        message = await database_sync_to_async(Message.objects.create)(
            sender=self.user,
            group=self.group,
            content=content
        )
        if 'attachments' in data:
            for attachment in data['attachments']:
                file_data = base64.b64decode(attachment['data'])
                file = ContentFile(file_data, name=attachment['name'])
                await database_sync_to_async(Attachment.objects.create)(
                    message=message,
                    file=file,
                    file_type=attachment['type']
                )
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'chat_message',
                'message': {
                    'id': message.id,
                    'sender': self.user.username,
                    'content': content,
                    'timestamp': message.timestamp.isoformat(),
                }
            }
        )
        cache.delete(f"messages_group_{self.group_id}")

    async def add_reaction(self, data):
        message_id = data['message_id']
        reaction_type = data['reaction_type']
        message = await database_sync_to_async(Message.objects.get)(id=message_id)
        await database_sync_to_async(Reaction.objects.get_or_create)(
            message=message,
            user=self.user,
            reaction_type=reaction_type
        )
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'reaction_added',
                'message_id': message_id,
                'reaction': reaction_type,
                'user': self.user.username
            }
        )

    async def delete_message(self, data):
        message_id = data['message_id']
        message = await database_sync_to_async(Message.objects.get)(id=message_id, sender=self.user)
        await database_sync_to_async(message.delete)()
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'message_deleted',
                'message_id': message_id
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event['message']))

    async def reaction_added(self, event):
        await self.send(text_data=json.dumps(event))

    async def message_deleted(self, event):
        await self.send(text_data=json.dumps(event))