import json
import logging  # Added for logger
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework_simplejwt.tokens import AccessToken, TokenError
from django.contrib.auth import get_user_model
from django.db.models import Q
from channels.db import database_sync_to_async
from messaging_app.models import (
    Message, MessageRequest, GroupChat, Reaction, Attachment
)
from messaging_app.serializers import MessageSerializer
from channels.generic.websocket import AsyncJsonWebsocketConsumer

# Define logger
logger = logging.getLogger(__name__)

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
        def _serialize():
            serializer = MessageSerializer(message, context={'request': None})
            return serializer.data
        return await database_sync_to_async(_serialize)()

    async def attach_files(self, message, attachment_ids):
        """Attach files to a message if provided"""
        if attachment_ids:
            def _attach_files():
                attachments = Attachment.objects.filter(id__in=attachment_ids)
                message.attachments.set(attachments)
                return True
            await database_sync_to_async(_attach_files)()

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
        
        # Join user's personal channel group for receiving broadcasts
        self.user_group_name = f'user_{self.user.id}'
        await self.channel_layer.group_add(self.user_group_name, self.channel_name)
        
        self.scope['user'] = self.user
        await self.accept()
        await self.send_json({'status': 'connected'})
        logger.info(f"User {self.user.id} connected to PrivateChatConsumer")

    async def disconnect(self, close_code):
        # Leave user's personal channel group
        if hasattr(self, 'user_group_name'):
            await self.channel_layer.group_discard(self.user_group_name, self.channel_name)
        user_id = getattr(self, 'user', None)
        user_id = user_id.id if user_id else 'unknown'
        logger.info(f"User {user_id} disconnected from PrivateChatConsumer")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get('action')
            logger.debug(f"Received action: {action}, data: {data}")
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
            else:
                await self.send_json({'error': f'Unknown action: {action}'})
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {str(e)}")
            await self.send_json({'error': 'Invalid JSON'})

    async def send_private_message(self, data):
        receiver_id = data.get('receiver_id')
        content = data.get('content')
        attachment_ids = data.get('attachment_ids', [])
        reply_to_id = data.get('reply_to_id')
        logger.info(f"Processing send_private_message: receiver_id={receiver_id}, content={content}, attachment_ids={attachment_ids}")
        
        # Validate required fields
        if not receiver_id:
            logger.error("Missing receiver_id in send_private_message")
            await self.send_json({'error': 'receiver_id is required'})
            return
            
        if not content and not attachment_ids:
            logger.error("Missing content and attachments in send_private_message")
            await self.send_json({'error': 'Message content or attachments are required'})
            return
        
        # Validate that user is not trying to send message to themselves
        if receiver_id == self.user.id:
            logger.warning(f"User {self.user.id} attempted to send message to themselves")
            await self.send_json({'error': 'Cannot send message to yourself'})
            return
            
        try:
            receiver = await database_sync_to_async(User.objects.get)(id=receiver_id)
            sender = self.user
            # Check existing conversation (either messages exist OR accepted message requests exist)
            messages_exist = await database_sync_to_async(
                lambda: Message.objects.filter(
                    (Q(sender=sender) & Q(receiver=receiver)) |
                    (Q(sender=receiver) & Q(receiver=sender))
                ).exists()
            )()
            
            accepted_requests_exist = await database_sync_to_async(
                lambda: MessageRequest.objects.filter(
                    (Q(sender=sender) & Q(receiver=receiver)) |
                    (Q(sender=receiver) & Q(receiver=sender)),
                    accepted=True
                ).exists()
            )()
            
            has_conversation = messages_exist or accepted_requests_exist
            logger.info(f"Conversation check - sender: {sender.id}, receiver: {receiver_id}, messages_exist: {messages_exist}, accepted_requests_exist: {accepted_requests_exist}, has_conversation: {has_conversation}")
            if not has_conversation:
                # Check if there's already a pending message request
                existing_request = await database_sync_to_async(
                    lambda: MessageRequest.objects.filter(
                        sender=sender, receiver=receiver, accepted=False
                    ).exists() or MessageRequest.objects.filter(
                        sender=receiver, receiver=sender, accepted=False
                    ).exists()
                )()
                
                if existing_request:
                    logger.info(f"Message request already exists between {sender.id} and {receiver_id}")
                    await self.send_json({'status': 'pending', 'message': 'Message request already sent'})
                    return
                
                logger.info(f"No existing conversation, creating message request for sender={sender.id}, receiver={receiver_id}")
                request = await database_sync_to_async(MessageRequest.objects.create)(
                    sender=sender, receiver=receiver, content=content
                )
                await self.send_json({'status': 'pending', 'message': 'Message request sent', 'request_id': str(request.id)})
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
            # Save the message to database
            logger.info(f"Creating message - sender: {sender.id}, receiver: {receiver.id}, content: {content[:50]}...")
            message = await database_sync_to_async(Message.objects.create)(
                sender=sender, receiver=receiver, content=content
            )
            logger.info(f"Message created successfully with ID: {message.id}, sender: {message.sender.id}, receiver: {message.receiver.id}")
            
            # Attach files if any
            await self.attach_files(message, attachment_ids)
            
            # Refresh message with all relationships for proper serialization
            def _refresh_message():
                return Message.objects.select_related('sender', 'receiver').prefetch_related('attachments', 'reactions').get(id=message.id)
            
            refreshed_message = await database_sync_to_async(_refresh_message)()
            serialized = await self.serialize_message(refreshed_message)
            
            logger.info(f"Broadcasting message to users: [{sender.id}, {receiver.id}]")
            await self.broadcast_to_users([sender.id, receiver.id], 'chat_message', {'message': serialized})
            await self.send_json({'status': 'success', 'message': serialized})
        except User.DoesNotExist:
            logger.error(f"Receiver not found: {receiver_id}")
            await self.send_json({'error': 'Receiver not found'})
        except Exception as e:
            logger.error(f"Error in send_private_message: {str(e)}")
            await self.send_json({'error': f'Server error: {str(e)}'})

    async def add_reaction(self, data):
        message_id = data.get('message_id')
        emoji = data.get('emoji')
        
        # Validate required fields
        if not message_id:
            await self.send_json({'error': 'message_id is required'})
            return
        if not emoji:
            await self.send_json({'error': 'emoji is required'})
            return
            
        try:
            message = await database_sync_to_async(Message.objects.get)(id=message_id)
            await database_sync_to_async(Reaction.objects.create)(
                message=message, user=self.user, emoji=emoji
            )
            await self.broadcast_to_users(
                [message.sender.id, message.receiver.id],
                'reaction_added',
                {'message_id': str(message.id), 'user_id': str(self.user.id), 'emoji': emoji}
            )
        except Message.DoesNotExist:
            await self.send_json({'error': 'Message not found'})
        except Exception as e:
            logger.error(f"Error in add_reaction: {str(e)}")
            await self.send_json({'error': f'Server error: {str(e)}'})

    async def edit_message(self, data):
        message_id = data.get('message_id')
        new_content = data.get('new_content')
        
        # Validate required fields
        if not message_id:
            await self.send_json({'error': 'message_id is required'})
            return
        if not new_content:
            await self.send_json({'error': 'new_content is required'})
            return
            
        try:
            message = await database_sync_to_async(Message.objects.get)(
                id=message_id, sender=self.user
            )
            message.content = new_content
            await database_sync_to_async(message.save)()
            await self.broadcast_to_users(
                [message.sender.id, message.receiver.id],
                'message_edited',
                {'message_id': str(message.id), 'new_content': new_content}
            )
        except Message.DoesNotExist:
            await self.send_json({'error': 'Cannot edit this message'})
        except Exception as e:
            logger.error(f"Error in edit_message: {str(e)}")
            await self.send_json({'error': f'Server error: {str(e)}'})

    async def delete_message(self, data):
        message_id = data.get('message_id')
        
        # Validate required fields
        if not message_id:
            await self.send_json({'error': 'message_id is required'})
            return
            
        try:
            message = await database_sync_to_async(Message.objects.get)(
                id=message_id, sender=self.user
            )
            await database_sync_to_async(message.delete)()
            await self.broadcast_to_users(
                [message.sender.id, message.receiver.id],
                'message_deleted',
                {'message_id': str(message.id)}
            )
        except Message.DoesNotExist:
            await self.send_json({'error': 'Cannot delete this message'})
        except Exception as e:
            logger.error(f"Error in delete_message: {str(e)}")
            await self.send_json({'error': f'Server error: {str(e)}'})

    async def mark_as_read(self, data):
        try:
            receiver_id = data.get('receiver_id')
            await database_sync_to_async(
                lambda: Message.objects.filter(sender_id=receiver_id, receiver=self.user, is_read=False)
                        .update(is_read=True)
            )()
            await self.broadcast_to_users(
                [receiver_id], 'messages_read', {'receiver_id': str(self.user.id)}
            )
        except Exception as e:
            logger.error(f"Error in mark_as_read: {str(e)}")
            await self.send_json({'error': f'Server error: {str(e)}'})

    async def notify_typing(self, data):
        try:
            await self.broadcast_to_users([data['receiver_id']], 'user_typing', {'user_id': self.user.id})
        except Exception as e:
            logger.error(f"Error in notify_typing: {str(e)}")

    async def notify_stop_typing(self, data):
        try:
            await self.broadcast_to_users([data['receiver_id']], 'user_stop_typing', {'user_id': self.user.id})
        except Exception as e:
            logger.error(f"Error in notify_stop_typing: {str(e)}")

    # Broadcast handlers
    async def chat_message(self, e): await self.send_json({'type': 'chat_message', **e})
    async def message_request(self, e): await self.send_json({'type': 'message_request', **e})
    async def request_accepted(self, e): await self.send_json({'type': 'request_accepted', **e})
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
            logger.info(f"User {self.user.id} connected to GroupChatConsumer for group {self.group_id}")

        except GroupChat.DoesNotExist:
            logger.error(f"Group {self.group_id} not found")
            await self.close()

    async def disconnect(self, close_code):
        # Leave group chat
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
        user_id = getattr(self, 'user', None)
        user_id = user_id.id if user_id else 'unknown'
        logger.info(f"User {user_id} disconnected from GroupChatConsumer")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get('action')
            logger.debug(f"Group chat received action: {action}, data: {data}")

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
            else:
                await self.send_json({'error': f'Unknown action: {action}'})
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in group chat: {str(e)}")
            await self.send_json({'error': 'Invalid JSON'})

    async def send_group_message(self, data):
        content = data.get('content')
        attachment_ids = data.get('attachment_ids', [])
        
        # Validate required fields
        if not content and not attachment_ids:
            logger.error("Missing content and attachments in send_group_message")
            await self.send_json({'error': 'Message content or attachments are required'})
            return
            
        try:
            group = await database_sync_to_async(GroupChat.objects.get)(id=self.group_id)
            message = await database_sync_to_async(Message.objects.create)(
                sender=self.user, group=group,
                content=content
            )
            await self.attach_files(message, data.get('attachment_ids', []))
            
            # Refresh message with all relationships for proper serialization
            def _refresh_message():
                return Message.objects.select_related('sender', 'group').prefetch_related('attachments', 'reactions').get(id=message.id)
            
            refreshed_message = await database_sync_to_async(_refresh_message)()
            serialized = await self.serialize_message(refreshed_message)
            
            await self.channel_layer.group_send(self.group_name, {'type': 'chat_message', 'message': serialized})
            await self.send_json({'status': 'success', 'message': serialized})
        except GroupChat.DoesNotExist:
            await self.send_json({'error': 'Group not found'})
        except Exception as e:
            logger.error(f"Error in send_group_message: {str(e)}")
            await self.send_json({'error': f'Server error: {str(e)}'})

    async def add_group_reaction(self, data):
        try:
            message = await database_sync_to_async(Message.objects.get)(
                id=data['message_id'], group_id=self.group_id
            )
            await database_sync_to_async(Reaction.objects.create)(
                message=message, user=self.user, emoji=data['emoji']
            )
            payload = {
                'message_id': str(message.id), 
                'user_id': str(self.user.id), 
                'emoji': data['emoji']
            }
            await self.channel_layer.group_send(
                self.group_name, 
                {'type': 'reaction_added', **payload}
            )
        except Message.DoesNotExist:
            await self.send_json({'error': 'Message not found or unauthorized'})
        except Exception as e:
            logger.error(f"Error in add_group_reaction: {str(e)}")
            await self.send_json({'error': f'Server error: {str(e)}'})

    async def edit_group_message(self, data):
        try:
            message = await database_sync_to_async(Message.objects.get)(
                id=data['message_id'], group_id=self.group_id, sender=self.user
            )
            message.content = data['new_content']
            await database_sync_to_async(message.save)()
            payload = {
                'message_id': str(message.id), 
                'new_content': data['new_content']
            }
            await self.channel_layer.group_send(
                self.group_name, 
                {'type': 'message_edited', **payload}
            )
        except Message.DoesNotExist:
            await self.send_json({'error': 'Message not found or unauthorized'})
        except Exception as e:
            logger.error(f"Error in edit_group_message: {str(e)}")
            await self.send_json({'error': f'Server error: {str(e)}'})

    async def delete_group_message(self, data):
        try:
            message = await database_sync_to_async(Message.objects.get)(
                id=data['message_id'], group_id=self.group_id, sender=self.user
            )
            message_id = str(message.id)
            await database_sync_to_async(message.delete)()
            payload = {'message_id': message_id}
            await self.channel_layer.group_send(
                self.group_name, 
                {'type': 'message_deleted', **payload}
            )
        except Message.DoesNotExist:
            await self.send_json({'error': 'Message not found or unauthorized'})
        except Exception as e:
            logger.error(f"Error in delete_group_message: {str(e)}")
            await self.send_json({'error': f'Server error: {str(e)}'})

    async def notify_typing(self, _=None):
        try:
            await self.channel_layer.group_send(self.group_name, {'type': 'user_typing', 'user_id': self.user.id})
        except Exception as e:
            logger.error(f"Error in notify_typing: {str(e)}")

    async def notify_stop_typing(self, _=None):
        try:
            await self.channel_layer.group_send(self.group_name, {'type': 'user_stop_typing', 'user_id': self.user.id})
        except Exception as e:
            logger.error(f"Error in notify_stop_typing: {str(e)}")

    # Group broadcast handlers
    async def chat_message(self, e): await self.send_json({'type': 'chat_message', **e})
    async def reaction_added(self, e): await self.send_json({'type': 'reaction_added', **e})
    async def message_edited(self, e): await self.send_json({'type': 'message_edited', **e})
    async def message_deleted(self, e): await self.send_json({'type': 'message_deleted', **e})
    async def user_typing(self, e): await self.send_json({'type': 'user_typing', **e})
    async def user_stop_typing(self, e): await self.send_json({'type': 'user_stop_typing', **e})

    # Utility to avoid repeating json.dumps
    async def send_json(self, data):
        await self.send(text_data=json.dumps(data))