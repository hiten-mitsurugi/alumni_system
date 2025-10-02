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

class GroupMembersView(APIView):
    """Dedicated view for fetching group members"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, group_id):
        """Get group members"""
        try:
            group = GroupChat.objects.get(id=group_id)
            if request.user not in group.members.all():
                return Response({'error': 'Not a member of this group'}, status=status.HTTP_403_FORBIDDEN)
            
            serializer = GroupChatSerializer(group, context={'request': request})
            return Response(serializer.data)
        except GroupChat.DoesNotExist:
            return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)
