from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from .models import Message, GroupChat, MessageRequest, BlockedUser, MutedConversation, UserProfile
from .serializers import MessageSerializer, GroupChatSerializer, UserSerializer, MessageRequestSerializer, BlockedUserSerializer, MutedConversationSerializer
from django.contrib.auth import get_user_model
from rest_framework import status
from django.db.models import Q
from django.utils import timezone

User = get_user_model()

class MessageListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, receiver_id=None, group_id=None):
        user = request.user
        if receiver_id:
            cache_key = f"messages_private_{user.id}_{receiver_id}"
            messages = cache.get(cache_key)
            if not messages:
                messages = Message.objects.filter(
                    (Q(sender=user) & Q(receiver_id=receiver_id)) |
                    (Q(sender_id=receiver_id) & Q(receiver=user))
                ).select_related('sender', 'receiver').prefetch_related('reactions', 'attachments')
                cache.set(cache_key, list(messages), timeout=3600)
            serializer = MessageSerializer(messages, many=True)
            return Response(serializer.data)
        elif group_id:
            cache_key = f"messages_group_{group_id}"
            messages = cache.get(cache_key)
            if not messages:
                messages = Message.objects.filter(group_id=group_id).select_related('sender').prefetch_related('reactions', 'attachments')
                cache.set(cache_key, list(messages), timeout=3600)
            serializer = MessageSerializer(messages, many=True)
            return Response(serializer.data)
        return Response({'error': 'Specify receiver_id or group_id'}, status=status.HTTP_400_BAD_REQUEST)

class GroupChatCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        name = request.data.get('name')
        member_ids = request.data.get('members', [])
        if not name or not member_ids:
            return Response({'error': 'Name and members required'}, status=status.HTTP_400_BAD_REQUEST)
        valid_members = User.objects.filter(id__in=member_ids).exclude(id=request.user.id)
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
        users = User.objects.filter(
            Q(sent_messages__receiver=user) | Q(received_messages__sender=user)
        ).distinct()
        serializer = UserSerializer(users, many=True)
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
        elif action == 'decline':
            msg_request.delete()
        return Response({'status': 'success'})

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
        users = User.objects.filter(username__icontains=query).exclude(id=request.user.id)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

class PinMessageView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, message_id):
        message = Message.objects.get(id=message_id)
        message.is_pinned = not message.is_pinned
        message.save()
        return Response({'status': 'message pinned/unpinned'})