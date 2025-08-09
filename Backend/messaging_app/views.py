from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from .models import Message, GroupChat, MessageRequest, BlockedUser, MutedConversation
from .serializers import UserSerializer, GroupChatSerializer, MessageSerializer, MessageRequestSerializer, BlockedUserSerializer, MutedConversationSerializer, AttachmentSerializer, ReactionSerializer, UserSearchSerializer
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .models import Attachment
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
import logging
from django.contrib.auth import get_user_model
CustomUser = get_user_model()

import logging
logger = logging.getLogger(__name__)

class SearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response({"users": [], "groups": []}, status=status.HTTP_200_OK)

        # ✅ Search users (safe filters)
        users_qs = CustomUser.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )

        # ✅ Apply optional filters if they exist
        if hasattr(CustomUser, 'is_approved'):
            users_qs = users_qs.filter(is_approved=True)
        if hasattr(CustomUser, 'user_type'):
            users_qs = users_qs.filter(user_type=3)

        users = users_qs.distinct()

        # ✅ Search groups
        groups = GroupChat.objects.filter(name__icontains=query)

        # ✅ Serialize using EXISTING serializers
        user_serializer = UserSearchSerializer(users, many=True, context={"request": request})
        group_serializer = GroupChatSerializer(groups, many=True)

        return Response({
            "users": user_serializer.data,
            "groups": group_serializer.data
        }, status=status.HTTP_200_OK)

        
        
class ConversationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        conversations = []

        # Private conversations (only with accepted contacts)
        private_users = CustomUser.objects.filter(
            Q(sent_messages__receiver=user) | Q(received_messages__sender=user)
        ).distinct()
        for other_user in private_users:
            latest_message = Message.objects.filter(
                (Q(sender=user) & Q(receiver=other_user)) |
                (Q(sender=other_user) & Q(receiver=user))
            ).order_by('-timestamp').first()
            if latest_message:
                unread_count = Message.objects.filter(
                    sender=other_user, receiver=user, is_read=False
                ).count()
                is_muted = MutedConversation.objects.filter(
                    user=user, receiver=other_user
                ).exists()
                is_blocked = BlockedUser.objects.filter(
                    user=user, blocked_user=other_user
                ).exists()
                conversations.append({
                    'type': 'private',
                    'id': str(other_user.id),
                    'mate': UserSearchSerializer(other_user, context={'request': request}).data,
                    'lastMessage': latest_message.content if latest_message else '',
                    'timestamp': latest_message.timestamp.isoformat() if latest_message else None,
                    'unreadCount': unread_count,
                    'isMuted': is_muted,
                    'isBlocked': is_blocked
                })

        # Group conversations
        groups = GroupChat.objects.filter(members=user)
        for group in groups:
            latest_message = Message.objects.filter(group=group).order_by('-timestamp').first()
            is_muted = MutedConversation.objects.filter(user=user, group=group).exists()
            conversations.append({
                'type': 'group',
                'id': str(group.id),
                'group': GroupChatSerializer(group).data,
                'lastMessage': latest_message.content if latest_message else '',
                'timestamp': latest_message.timestamp.isoformat() if latest_message else None,
                'unreadCount': 0,  # Placeholder; enhance later
                'isMuted': is_muted
            })

        conversations.sort(key=lambda x: x['timestamp'] or '1970-01-01T00:00:00Z', reverse=True)
        return Response(conversations)

class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        receiver_id = request.data.get('receiver_id')
        content = request.data.get('content')
        reply_to_id = request.data.get('reply_to_id')
        attachment_ids = request.data.get('attachment_ids', [])

        if not receiver_id or not content:
            return Response({'error': 'Receiver ID and content required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            receiver = CustomUser.objects.get(id=receiver_id)
        except settings.AUTH_USER_MODEL.DoesNotExist:
            return Response({'error': 'Receiver not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if receiver has blocked the sender
        if BlockedUser.objects.filter(user=receiver, blocked_user=request.user).exists():
            return Response({'error': 'You are blocked by this user'}, status=status.HTTP_403_FORBIDDEN)

        # Check if there's an existing conversation (either messages exist OR accepted message requests exist)
        has_conversation = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=receiver)) |
            (Q(sender=receiver) & Q(receiver=request.user))
        ).exists() or MessageRequest.objects.filter(
            (Q(sender=request.user) & Q(receiver=receiver)) |
            (Q(sender=receiver) & Q(receiver=request.user)),
            accepted=True
        ).exists()

        if not has_conversation:
            # Create a message request if no prior conversation
            message_request = MessageRequest.objects.create(
                sender=request.user,
                receiver=receiver,
                content=content,
                timestamp=timezone.now()
            )
            return Response({
                'status': 'Message request sent',
                'request_id': str(message_request.id)
            }, status=status.HTTP_201_CREATED)
        else:
            # Create message if conversation exists
            message = Message.objects.create(
                sender=request.user,
                receiver=receiver,
                content=content
            )
            for attachment_id in attachment_ids:
                attachment = Attachment.objects.get(id=attachment_id)
                message.attachments.add(attachment)
            serializer = MessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

class MessageListView(APIView):
    def get(self, request, receiver_id=None, group_id=None):
        # ✅ Try UUID lookup first
        receiver = None
        try:
            receiver = CustomUser.objects.get(id=receiver_id)
        except (CustomUser.DoesNotExist, ValueError):
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Fetch messages as usual...
        messages = Message.objects.filter(
            sender=request.user, receiver=receiver
        ) | Message.objects.filter(
            sender=receiver, receiver=request.user
        )
        messages = messages.order_by("timestamp")

        serializer = MessageSerializer(messages, many=True, context={'request': request})
        return Response(serializer.data)

class GroupChatCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        name = request.data.get('name')
        member_ids = request.data.get('members', [])
        if not name or not member_ids:
            return Response({'error': 'Name and members required'}, status=status.HTTP_400_BAD_REQUEST)
        valid_members = settings.AUTH_USER_MODEL.objects.filter(id__in=member_ids).exclude(id=request.user.id)
        group = GroupChat.objects.create(name=name)
        group.members.add(request.user, *valid_members)
        group.admins.add(request.user)
        serializer = GroupChatSerializer(group)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class GroupChatManageView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, group_id):
        group = GroupChat.objects.get(id=group_id)
        if request.user not in group.admins.all():
            return Response({'error': 'Not an admin'}, status=status.HTTP_403_FORBIDDEN)
        action = request.data.get('action')
        user_id = request.data.get('user_id')
        if action == 'add_member':
            group.members.add(user_id)
        elif action == 'remove_member':
            group.members.remove(user_id)
        elif action == 'promote_admin':
            group.admins.add(user_id)
        elif action == 'demote_admin':
            group.admins.remove(user_id)
        serializer = GroupChatSerializer(group)
        return Response(serializer.data)

class GroupChatListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        groups = GroupChat.objects.filter(members=request.user)
        serializer = GroupChatSerializer(groups, many=True)
        return Response(serializer.data)

class ConversationUsersView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        users = settings.AUTH_USER_MODEL.objects.filter(
            Q(sent_messages__receiver=user) | Q(received_messages__sender=user)
        ).distinct()
        serializer = UserSearchSerializer(users, many=True, context={'request': request})
        return Response(serializer.data)

class MessageRequestView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        requests = MessageRequest.objects.filter(receiver=request.user, accepted=False)
        serializer = MessageRequestSerializer(requests, many=True)
        return Response(serializer.data)
    def post(self, request):
        action = request.data.get('action')
        request_id = request.data.get('request_id')
        msg_request = MessageRequest.objects.get(id=request_id, receiver=request.user)
        if action == 'accept':
            msg_request.accepted = True
            msg_request.save()
            # Create a message with the original content from the request
            message = Message.objects.create(
                sender=msg_request.sender,
                receiver=request.user,
                content=msg_request.content  # Use the actual message content
            )
            
            # Send real-time notification to sender that request was accepted
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'user_{msg_request.sender.id}',
                {
                    'type': 'request_accepted',
                    'message': {
                        'id': str(message.id),
                        'content': message.content,
                        'receiver': {'id': request.user.id, 'first_name': request.user.first_name},
                        'timestamp': message.timestamp.isoformat()
                    }
                }
            )
            
            return Response({'status': 'Request accepted', 'message_id': str(message.id)})
        elif action == 'decline':
            msg_request.delete()
            return Response({'status': 'Request declined'})
        return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

class BlockUserView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        blocked_users = BlockedUser.objects.filter(user=request.user)
        serializer = BlockedUserSerializer(blocked_users, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        user_id = request.data.get('user_id')
        BlockedUser.objects.create(user=request.user, blocked_user_id=user_id)
        return Response({'status': 'user blocked'})
        
    def delete(self, request, user_id):
        BlockedUser.objects.filter(user=request.user, blocked_user_id=user_id).delete()
        return Response({'status': 'user unblocked'})

class MuteConversationView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        muted_conversations = MutedConversation.objects.filter(user=request.user)
        serializer = MutedConversationSerializer(muted_conversations, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        receiver_id = request.data.get('receiver_id')
        group_id = request.data.get('group_id')
        muted_until = request.data.get('muted_until')
        MutedConversation.objects.create(
            user=request.user,
            receiver_id=receiver_id if receiver_id else None,
            group_id=group_id if group_id else None,
            muted_until=muted_until
        )
        return Response({'status': 'conversation muted'})
    
    def delete(self, request):
        receiver_id = request.data.get('receiver_id')
        group_id = request.data.get('group_id')
        
        muted_conversation = MutedConversation.objects.filter(
            user=request.user,
            receiver_id=receiver_id if receiver_id else None,
            group_id=group_id if group_id else None
        ).first()
        
        if muted_conversation:
            muted_conversation.delete()
            return Response({'status': 'conversation unmuted'})
        return Response({'error': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)

class SearchUsersView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        query = request.GET.get('q', '')
        users = settings.AUTH_USER_MODEL.objects.filter(
            Q(username__icontains=query) | 
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query)
        ).exclude(id=request.user.id)
        serializer = UserSearchSerializer(users, many=True, context={'request': request})
        return Response(serializer.data)

class PinMessageView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, message_id):
        """Pin or unpin a message"""
        try:
            message = get_object_or_404(Message, id=message_id)
            
            # Check if user has permission to pin this message
            # For private messages: either sender or receiver can pin
            # For group messages: any group member can pin
            can_pin = False
            
            if message.receiver:  # Private message
                if request.user == message.sender or request.user == message.receiver:
                    can_pin = True
            elif message.group:  # Group message
                if request.user in message.group.members.all():
                    can_pin = True
            
            if not can_pin:
                return Response({
                    'error': 'You do not have permission to pin this message'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Toggle pin status
            message.is_pinned = not message.is_pinned
            message.save()
            
            # Send real-time notification via WebSocket
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            
            channel_layer = get_channel_layer()
            
            # Prepare message data for WebSocket
            serializer = MessageSerializer(message, context={'request': request})
            
            if message.receiver:  # Private message
                # Notify both sender and receiver
                for user_id in [message.sender.id, message.receiver.id]:
                    async_to_sync(channel_layer.group_send)(
                        f'user_{user_id}',
                        {
                            'type': 'message_pinned',
                            'message': serializer.data,
                            'action': 'pin' if message.is_pinned else 'unpin'
                        }
                    )
            elif message.group:  # Group message
                # Notify all group members
                async_to_sync(channel_layer.group_send)(
                    f'group_{message.group.id}',
                    {
                        'type': 'message_pinned',
                        'message': serializer.data,
                        'action': 'pin' if message.is_pinned else 'unpin'
                    }
                )
            
            return Response({
                'status': f'Message {"pinned" if message.is_pinned else "unpinned"} successfully',
                'message': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error pinning/unpinning message {message_id}: {e}")
            return Response({
                'error': 'Failed to pin/unpin message'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class BumpMessageView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, message_id):
        """
        Bump a message - creates a new message that references the original.
        Like Facebook Messenger's bump feature.
        """
        try:
            # Get the original message - must be sender's own message
            original_message = get_object_or_404(
                Message, 
                id=message_id, 
                sender=request.user
            )
            
            # Determine the receiver based on original message type
            if original_message.receiver:
                # Private message - bump to same receiver
                receiver = original_message.receiver
                group = None
            elif original_message.group:
                # Group message - bump to same group
                receiver = None
                group = original_message.group
                
                # Check if user is still a member of the group
                if request.user not in group.members.all():
                    return Response({
                        'error': 'You are no longer a member of this group'
                    }, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({
                    'error': 'Invalid message type'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create the bump message
            bump_message = Message.objects.create(
                sender=request.user,
                receiver=receiver,
                group=group,
                content=f"🔔 Bumped message",  # Special content indicating this is a bump
                reply_to=original_message  # Reference to original message
            )
            
            # Serialize the new bump message with full relationships
            bump_message_with_relations = Message.objects.select_related(
                'sender', 'receiver', 'group', 'reply_to', 'reply_to__sender'
            ).prefetch_related('attachments').get(id=bump_message.id)
            
            serializer = MessageSerializer(
                bump_message_with_relations, 
                context={'request': request}
            )
            
            # Send real-time notification via WebSocket
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            
            channel_layer = get_channel_layer()
            
            if receiver:
                # Private message bump - notify receiver
                async_to_sync(channel_layer.group_send)(
                    f'user_{receiver.id}',
                    {
                        'type': 'chat_message',
                        'message': serializer.data
                    }
                )
                # Also notify sender for real-time update
                async_to_sync(channel_layer.group_send)(
                    f'user_{request.user.id}',
                    {
                        'type': 'chat_message',
                        'message': serializer.data
                    }
                )
            elif group:
                # Group message bump - notify all group members
                async_to_sync(channel_layer.group_send)(
                    f'group_{group.id}',
                    {
                        'type': 'chat_message',
                        'message': serializer.data
                    }
                )
            
            return Response({
                'status': 'Message bumped successfully',
                'message': serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error bumping message {message_id}: {e}")
            return Response({
                'error': 'Failed to bump message'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UploadView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        file = request.FILES['file']
        # Create attachment directly like profile picture upload
        attachment = Attachment.objects.create(
            file=file,
            file_type=file.content_type
        )
        return Response({'id': str(attachment.id)}, status=status.HTTP_201_CREATED)