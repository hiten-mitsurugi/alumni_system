from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from .models import Message, GroupChat, Reaction, Attachment
from django.contrib.auth import get_user_model
from rest_framework import status

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
                    (models.Q(sender=user) & models.Q(receiver_id=receiver_id)) |
                    (models.Q(sender_id=receiver_id) & models.Q(receiver=user))
                ).select_related('sender', 'receiver').prefetch_related('reactions', 'attachments')
                cache.set(cache_key, list(messages), timeout=3600)
            data = [{'id': m.id, 'sender': m.sender.username, 'content': m.content, 'timestamp': m.timestamp.isoformat(),
                     'reactions': [{'type': r.reaction_type, 'user': r.user.username} for r in m.reactions.all()],
                     'attachments': [{'url': a.file.url, 'type': a.file_type} for a in m.attachments.all()]} for m in messages]
            return Response(data)
        elif group_id:
            cache_key = f"messages_group_{group_id}"
            messages = cache.get(cache_key)
            if not messages:
                messages = Message.objects.filter(group_id=group_id).select_related('sender').prefetch_related('reactions', 'attachments')
                cache.set(cache_key, list(messages), timeout=3600)
            data = [{'id': m.id, 'sender': m.sender.username, 'content': m.content, 'timestamp': m.timestamp.isoformat(),
                     'reactions': [{'type': r.reaction_type, 'user': r.user.username} for r in m.reactions.all()],
                     'attachments': [{'url': a.file.url, 'type': a.file_type} for a in m.attachments.all()]} for m in messages]
            return Response(data)
        return Response({'error': 'Specify receiver_id or group_id'}, status=status.HTTP_400_BAD_REQUEST)

class GroupChatCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        name = request.data.get('name')
        member_ids = request.data.get('members', [])
        group = GroupChat.objects.create(name=name)
        group.members.add(request.user, *User.objects.filter(id__in=member_ids))
        group.admins.add(request.user)
        return Response({'group_id': group.id}, status=status.HTTP_201_CREATED)

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
        return Response({'message': 'Action completed'}, status=status.HTTP_200_OK)