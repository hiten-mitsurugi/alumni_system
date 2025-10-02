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

class SearchUsersView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        query = request.GET.get('q', '')
        
        # Get blocked users to exclude from search
        blocked_user_ids = BlockedUser.objects.filter(user=request.user).values_list('blocked_user_id', flat=True)
        blocked_by_user_ids = BlockedUser.objects.filter(blocked_user=request.user).values_list('user_id', flat=True)
        
        # Combine both lists to exclude all blocked relationships
        excluded_user_ids = list(blocked_user_ids) + list(blocked_by_user_ids)
        
        users = User.objects.filter(
            Q(username__icontains=query) | 
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query)
        ).exclude(
            id=request.user.id  # Exclude self
        ).exclude(
            id__in=excluded_user_ids  # Exclude blocked users
        )
        
        serializer = UserSearchSerializer(users, many=True, context={'request': request})
        return Response(serializer.data)
