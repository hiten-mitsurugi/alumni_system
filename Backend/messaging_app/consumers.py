import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken, TokenError
from .models import Message, GroupChat, Reaction, Attachment
from .serializers import MessageSerializer
from django.core.files.base import ContentFile
import base64
from django.core.cache import cache

User = get_user_model()

class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Extract token from query string
        query_string = self.scope['query_string'].decode()
        token = None
        for param in query_string.split('&'):
            if param.startswith('token='):
                token = param[len('token='):]
                break

        if not token:
            print("No token provided in WebSocket connection")
            await self.close(code=4001)
            return

        try:
            # Validate JWT token
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            self.user = await database_sync_to_async(User.objects.get)(id=user_id)
        except (TokenError, User.DoesNotExist) as e:
            print(f"Token validation failed: {str(e)}")
            await self.close(code=4003)
            return

        if not self.user.is_authenticated:
            print("User is not authenticated")
            await self.close(code=4003)
            return

        self.group_name = f"private_{self.user.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        print(f"WebSocket connected for user {self.user.username}")

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            print(f"WebSocket disconnected for user {self.user.username}")

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
        try:
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
            message_data = await database_sync_to_async(MessageSerializer)(message).data
            await self.channel_layer.group_send(
                f"private_{receiver_id}",
                {
                    'type': 'chat_message',
                    'message': message_data
                }
            )
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat_message',
                    'message': message_data
                }
            )
            cache.delete(f"messages_private_{self.user.id}_{receiver_id}")
        except User.DoesNotExist:
            await self.send(text_data=json.dumps({
                'status': 'error',
                'message': 'Receiver does not exist'
            }))

    async def add_reaction(self, data):
        message_id = data['message_id']
        reaction_type = data['reaction_type']
        try:
            message = await database_sync_to_async(Message.objects.get)(id=message_id)
            reaction = await database_sync_to_async(Reaction.objects.get_or_create)(
                message=message,
                user=self.user,
                reaction_type=reaction_type
            )[0]
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
        except Message.DoesNotExist:
            await self.send(text_data=json.dumps({
                'status': 'error',
                'message': 'Message does not exist'
            }))

    async def delete_message(self, data):
        message_id = data['message_id']
        try:
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
        except Message.DoesNotExist:
            await self.send(text_data=json.dumps({
                'status': 'error',
                'message': 'Message does not exist or not authorized'
            }))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message']
        }))

    async def reaction_added(self, event):
        await self.send(text_data=json.dumps({
            'type': 'reaction_added',
            'message_id': event['message_id'],
            'reaction': event['reaction'],
            'user': event['user']
        }))

    async def message_deleted(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message_deleted',
            'message_id': event['message_id']
        }))

class GroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Extract token from query string
        query_string = self.scope['query_string'].decode()
        token = None
        for param in query_string.split('&'):
            if param.startswith('token='):
                token = param[len('token='):]
                break

        if not token:
            print("No token provided in WebSocket connection")
            await self.close(code=4001)
            return

        try:
            # Validate JWT token
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            self.user = await database_sync_to_async(User.objects.get)(id=user_id)
        except (TokenError, User.DoesNotExist) as e:
            print(f"Token validation failed: {str(e)}")
            await self.close(code=4003)
            return

        if not self.user.is_authenticated:
            print("User is not authenticated")
            await self.close(code=4003)
            return

        self.group_id = self.scope['url_route']['kwargs']['group_id']
        try:
            self.group = await database_sync_to_async(GroupChat.objects.get)(id=self.group_id)
            if self.user not in await database_sync_to_async(self.group.members.all)():
                print(f"User {self.user.username} is not a member of group {self.group_id}")
                await self.close(code=4004)
                return
            self.group_name = f"group_{self.group_id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            print(f"WebSocket connected for group {self.group_id}, user {self.user.username}")
        except GroupChat.DoesNotExist:
            print(f"Group {self.group_id} does not exist")
            await self.close(code=4005)

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            print(f"WebSocket disconnected for group {self.group_id}, user {self.user.username}")

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
        try:
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
            message_data = await database_sync_to_async(MessageSerializer)(message).data
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat_message',
                    'message': message_data
                }
            )
            cache.delete(f"messages_group_{self.group_id}")
        except Exception as e:
            await self.send(text_data=json.dumps({
                'status': 'error',
                'message': str(e)
            }))

    async def add_reaction(self, data):
        message_id = data['message_id']
        reaction_type = data['reaction_type']
        try:
            message = await database_sync_to_async(Message.objects.get)(id=message_id)
            reaction = await database_sync_to_async(Reaction.objects.get_or_create)(
                message=message,
                user=self.user,
                reaction_type=reaction_type
            )[0]
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'reaction_added',
                    'message_id': message_id,
                    'reaction': reaction_type,
                    'user': self.user.username
                }
            )
        except Message.DoesNotExist:
            await self.send(text_data=json.dumps({
                'status': 'error',
                'message': 'Message does not exist'
            }))

    async def delete_message(self, data):
        message_id = data['message_id']
        try:
            message = await database_sync_to_async(Message.objects.get)(id=message_id, sender=self.user)
            await database_sync_to_async(message.delete)()
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'message_deleted',
                    'message_id': message_id
                }
            )
        except Message.DoesNotExist:
            await self.send(text_data=json.dumps({
                'status': 'error',
                'message': 'Message does not exist or not authorized'
            }))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message']
        }))

    async def reaction_added(self, event):
        await self.send(text_data=json.dumps({
            'type': 'reaction_added',
            'message_id': event['message_id'],
            'reaction': event['reaction'],
            'user': event['user']
        }))

    async def message_deleted(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message_deleted',
            'message_id': event['message_id']
        }))