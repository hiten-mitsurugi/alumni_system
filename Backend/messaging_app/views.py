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
    def post(self, request):
        user_id = request.data.get('user_id')
        BlockedUser.objects.create(user=request.user, blocked_user_id=user_id)
        return Response({'status': 'user blocked'})
    def delete(self, request, user_id):
        BlockedUser.objects.filter(user=request.user, blocked_user_id=user_id).delete()
        return Response({'status': 'user unblocked'})

class MuteConversationView(APIView):
    permission_classes = [IsAuthenticated]
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
        message = Message.objects.get(id=message_id)
        message.is_pinned = not message.is_pinned
        message.save()
        return Response({'status': 'message pinned/unpinned'})
    
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