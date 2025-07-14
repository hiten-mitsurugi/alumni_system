import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken, TokenError
from .models import Message, GroupChat, Reaction, Attachment, MessageRequest, BlockedUser
from .serializers import MessageSerializer
from django.core.files.base import ContentFile
import base64
from django.core.cache import cache

User = get_user_model()

class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        query_string = self.scope['query_string'].decode()
        token = next((param.split('=')[1] for param in query_string.split('&') if param.startswith('token=')), None)
        if not token:
            await self.close(code=4001)
            return
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            self.user = await database_sync_to_async(User.objects.get)(id=user_id)
        except (TokenError, User.DoesNotExist):
            await self.close(code=4003)
            return
        self.group_name = f"private_{self.user.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await database_sync_to_async(self.user.profile.update)(status='online')

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            await database_sync_to_async(self.user.profile.update)(status='offline', last_seen=timezone.now())

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        if action == 'send_message':
            await self.send_private_message(data)
        elif action == 'react':
            await self.add_reaction(data)
        elif action == 'delete':
            await self.delete_message(data)
        elif action == 'edit_message':
            await self.edit_message(data)
        elif action == 'typing':
            await self.channel_layer.group_send(f"private_{data['receiver_id']}", {'type': 'user_typing', 'user': self.user.username})
        elif action == 'stop_typing':
            await self.channel_layer.group_send(f"private_{data['receiver_id']}", {'type': 'user_stop_typing', 'user': self.user.username})
        elif action == 'mark_as_read':
            await self.mark_as_read(data)

    async def send_private_message(self, data):
        receiver_id = data.get('receiver_id')
        content = data.get('content', '')
        reply_to_id = data.get('reply_to_id')
        receiver = await database_sync_to_async(User.objects.get)(id=receiver_id)
        if await database_sync_to_async(BlockedUser.objects.filter(user=receiver, blocked_user=self.user).exists)():
            await self.send(text_data=json.dumps({'status': 'error', 'message': 'You are blocked'}))
            return
        if not await database_sync_to_async(MessageRequest.objects.filter(sender=self.user, receiver=receiver, accepted=True).exists)():
            await database_sync_to_async(MessageRequest.objects.get_or_create)(sender=self.user, receiver=receiver)
            await self.send(text_data=json.dumps({'status': 'pending', 'message': 'Message request sent'}))
            return
        message = await database_sync_to_async(Message.objects.create)(
            sender=self.user, receiver=receiver, content=content,
            reply_to_id=reply_to_id if reply_to_id else None
        )
        if 'attachments' in data:
            for attachment in data['attachments']:
                file_data = base64.b64decode(attachment['data'])
                file = ContentFile(file_data, name=attachment['name'])
                await database_sync_to_async(Attachment.objects.create)(message=message, file=file, file_type=attachment['type'])
        message_data = await database_sync_to_async(lambda: MessageSerializer(message).data)()
        await self.channel_layer.group_send(f"private_{receiver_id}", {'type': 'chat_message', 'message': message_data})
        await self.channel_layer.group_send(self.group_name, {'type': 'chat_message', 'message': message_data})
        cache.delete(f"messages_private_{self.user.id}_{receiver_id}")

    async def edit_message(self, data):
        message_id = data.get('message_id')
        new_content = data.get('new_content')
        message = await database_sync_to_async(Message.objects.get)(id=message_id, sender=self.user)
        message.content = new_content
        await database_sync_to_async(message.save)()
        target = f"private_{message.receiver.id}"
        await self.channel_layer.group_send(target, {'type': 'message_edited', 'message_id': message_id, 'new_content': new_content})

    async def mark_as_read(self, data):
        receiver_id = data.get('receiver_id')
        await database_sync_to_async(Message.objects.filter(sender_id=receiver_id, receiver=self.user, is_read=False).update)(is_read=True)
        await self.channel_layer.group_send(f"private_{receiver_id}", {'type': 'messages_read', 'receiver_id': self.user.id})

    # Existing methods: add_reaction, delete_message, chat_message, reaction_added, message_deleted remain unchanged
    async def user_typing(self, event):
        await self.send(text_data=json.dumps({'type': 'user_typing', 'user': event['user']}))
    async def user_stop_typing(self, event):
        await self.send(text_data=json.dumps({'type': 'user_stop_typing', 'user': event['user']}))
    async def message_edited(self, event):
        await self.send(text_data=json.dumps({'type': 'message_edited', 'message_id': event['message_id'], 'new_content': event['new_content']}))
    async def messages_read(self, event):
        await self.send(text_data=json.dumps({'type': 'messages_read', 'receiver_id': event['receiver_id']}))

class GroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        query_string = self.scope['query_string'].decode()
        token = next((param.split('=')[1] for param in query_string.split('&') if param.startswith('token=')), None)
        if not token:
            await self.close(code=4001)
            return
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            self.user = await database_sync_to_async(User.objects.get)(id=user_id)
        except (TokenError, User.DoesNotExist):
            await self.close(code=4003)
            return
        self.group_id = self.scope['url_route']['kwargs']['group_id']
        self.group = await database_sync_to_async(GroupChat.objects.get)(id=self.group_id)
        if self.user not in await database_sync_to_async(list)(self.group.members.all()):
            await self.close(code=4004)
            return
        self.group_name = f"group_{self.group_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        if action == 'send_message':
            await self.send_group_message(data)
        elif action == 'react':
            await self.add_reaction(data)
        elif action == 'delete':
            await self.delete_message(data)
        elif action == 'edit_message':
            await self.edit_message(data)
        elif action == 'typing':
            await self.channel_layer.group_send(self.group_name, {'type': 'user_typing', 'user': self.user.username})
        elif action == 'stop_typing':
            await self.channel_layer.group_send(self.group_name, {'type': 'user_stop_typing', 'user': self.user.username})

    async def send_group_message(self, data):
        content = data.get('content', '')
        reply_to_id = data.get('reply_to_id')
        message = await database_sync_to_async(Message.objects.create)(
            sender=self.user, group=self.group, content=content,
            reply_to_id=reply_to_id if reply_to_id else None
        )
        if 'attachments' in data:
            for attachment in data['attachments']:
                file_data = base64.b64decode(attachment['data'])
                file = ContentFile(file_data, name=attachment['name'])
                await database_sync_to_async(Attachment.objects.create)(message=message, file=file, file_type=attachment['type'])
        message_data = await database_sync_to_async(lambda: MessageSerializer(message).data)()
        await self.channel_layer.group_send(self.group_name, {'type': 'chat_message', 'message': message_data})
        cache.delete(f"messages_group_{self.group_id}")

    async def edit_message(self, data):
        message_id = data.get('message_id')
        new_content = data.get('new_content')
        message = await database_sync_to_async(Message.objects.get)(id=message_id, sender=self.user)
        message.content = new_content
        await database_sync_to_async(message.save)()
        await self.channel_layer.group_send(self.group_name, {'type': 'message_edited', 'message_id': message_id, 'new_content': new_content})

    # Existing methods: add_reaction, delete_message, chat_message, reaction_added, message_deleted remain unchanged
    async def user_typing(self, event):
        await self.send(text_data=json.dumps({'type': 'user_typing', 'user': event['user']}))
    async def user_stop_typing(self, event):
        await self.send(text_data=json.dumps({'type': 'user_stop_typing', 'user': event['user']}))
    async def message_edited(self, event):
        await self.send(text_data=json.dumps({'type': 'message_edited', 'message_id': event['message_id'], 'new_content': event['new_content']}))