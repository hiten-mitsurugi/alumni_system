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

class GroupChatListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        current_user = request.user
        
        # 🚀 SPEED: Try to get cached group conversations first
        cache_key = f"user_group_conversations_{current_user.id}"
        cached_groups = cache.get(cache_key)
        
        if cached_groups:
            logger.info(f"🚀 Cache HIT: Returning cached group conversations for user {current_user.id}")
            return Response(cached_groups)
        
        # 🚀 SPEED: Optimized query with prefetch_related
        groups = GroupChat.objects.filter(members=current_user).prefetch_related(
            'members', 'admins'
        ).select_related()
        
        # Transform groups to include unread count and last message info
        group_conversations = []
        for group in groups:
            # 🚀 SPEED: Get the latest message in this group
            latest_message = Message.objects.filter(group=group).select_related('sender').order_by('-timestamp').first()
            
            # 🚀 SPEED: Calculate unread count for this user in this group
            # Similar to private messages: count messages from others that this user hasn't "read"
            # A message is considered "read" if there's a MessageRead record for this user
            unread_messages = Message.objects.filter(
                group=group
            ).exclude(sender=current_user)
            
            read_message_ids = MessageRead.objects.filter(
                user=current_user,
                message__group=group
            ).values_list('message_id', flat=True)
            
            unread_count = unread_messages.exclude(id__in=read_message_ids).count()
            
            # Build group conversation object
            group_data = {
                'id': group.id,
                'type': 'group',
                'group': {
                    'id': group.id,
                    'name': group.name,
                    'description': group.description,
                    'group_picture': request.build_absolute_uri(group.group_picture.url) if group.group_picture else None,
                    'members': [
                        {
                            'id': member.id,
                            'username': member.username,
                            'first_name': member.first_name,
                            'last_name': member.last_name,
                            'profile_picture': request.build_absolute_uri(member.profile_picture.url) if member.profile_picture else None
                        } for member in group.members.all()
                    ],
                    'admins': [admin.id for admin in group.admins.all()],
                    'created_at': group.created_at.isoformat(),
                    'updated_at': group.updated_at.isoformat()
                },
                'lastMessage': latest_message.content[:50] + ('...' if latest_message and len(latest_message.content) > 50 else '') if latest_message else 'No messages yet',
                'timestamp': latest_message.timestamp.isoformat() if latest_message else group.created_at.isoformat(),
                'unreadCount': unread_count
            }
            group_conversations.append(group_data)
        
        # Sort by timestamp (newest first)
        group_conversations.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # 🚀 SPEED: Cache for 10 seconds (group conversations change frequently)
        cache.set(cache_key, group_conversations, 10)
        logger.info(f"🚀 Cache MISS: Cached group conversations for user {current_user.id}")
        
        return Response(group_conversations)
