from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache

from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from ..models import Message, GroupChat, MessageRequest, BlockedUser, GroupMemberRequest, MessageRead
from ..serializers import UserSerializer, GroupChatSerializer, MessageSerializer, MessageRequestSerializer, BlockedUserSerializer, AttachmentSerializer, ReactionSerializer, UserSearchSerializer, GroupMemberRequestSerializer
from ..link_utils import create_link_previews_for_message
import logging
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import uuid

# Initialize logger
logger = logging.getLogger(__name__)
from ..models import Attachment
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

class SearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response({"users": [], "groups": []}, status=status.HTTP_200_OK)

        # Get blocked users to mark them as blocked (but still show them in search)
        blocked_user_ids = BlockedUser.objects.filter(user=request.user).values_list('blocked_user_id', flat=True)
        blocked_by_user_ids = BlockedUser.objects.filter(blocked_user=request.user).values_list('user_id', flat=True)

        # ✅ Search users (show all users, don't exclude blocked ones)
        users_qs = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).exclude(
            id=request.user.id  # Only exclude self
        )

        # ✅ Apply optional filters if they exist
        if hasattr(User, 'is_approved'):
            users_qs = users_qs.filter(is_approved=True)
        if hasattr(User, 'user_type'):
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
