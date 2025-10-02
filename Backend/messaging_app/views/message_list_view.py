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

class MessageListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, receiver_id=None, group_id=None):
        if group_id:
            # Handle group messages with Redis caching
            try:
                group = GroupChat.objects.get(id=group_id)
                # Check if user is a member of the group
                if request.user not in group.members.all():
                    return Response({"error": "You are not a member of this group"}, status=status.HTTP_403_FORBIDDEN)
                
                # 🚀 SPEED: Try to get cached group messages first
                cache_key = f"group_messages_{group_id}_{request.user.id}"
                cached_messages = cache.get(cache_key)
                
                if cached_messages:
                    logger.info(f"🚀 Cache HIT: Returning cached group messages for group {group_id}")
                    return Response(cached_messages)
                
                # Fetch group messages with optimized query
                messages = Message.objects.filter(group=group).select_related(
                    'sender', 'sender__profile', 'reply_to', 'reply_to__sender'
                ).prefetch_related(
                    'attachments', 'reactions', 'reactions__user'
                ).order_by("timestamp")
                
                serializer = MessageSerializer(messages, many=True, context={'request': request})
                serialized_data = serializer.data
                
                # 🚀 SPEED: Cache for 30 seconds (messages change frequently)
                cache.set(cache_key, serialized_data, 30)
                logger.info(f"🚀 Cache MISS: Cached group messages for group {group_id}")
                
                return Response(serialized_data)
                
            except GroupChat.DoesNotExist:
                return Response({"error": "Group not found"}, status=status.HTTP_404_NOT_FOUND)
        
        elif receiver_id:
            # Handle private messages with Redis caching
            try:
                receiver = User.objects.get(id=receiver_id)
            except (User.DoesNotExist, ValueError):
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            # 🚀 SPEED: Try to get cached private messages first
            # Use sorted IDs to ensure same cache key regardless of sender/receiver order
            user_ids = sorted([request.user.id, receiver_id])
            cache_key = f"private_messages_{user_ids[0]}_{user_ids[1]}"
            cached_messages = cache.get(cache_key)
            
            if cached_messages:
                logger.info(f"🚀 Cache HIT: Returning cached private messages for users {user_ids}")
                return Response(cached_messages)

            # Don't block message viewing - let users see their conversation history
            # Only block sending new messages (handled in SendMessageView)
            
            # Fetch messages with optimized query
            messages = Message.objects.filter(
                sender=request.user, receiver=receiver
            ) | Message.objects.filter(
                sender=receiver, receiver=request.user
            )
            messages = messages.select_related(
                'sender', 'sender__profile', 'receiver', 'receiver__profile', 
                'reply_to', 'reply_to__sender'
            ).prefetch_related(
                'attachments', 'reactions', 'reactions__user'
            ).order_by("timestamp")

            serializer = MessageSerializer(messages, many=True, context={'request': request})
            serialized_data = serializer.data
            
            # 🚀 SPEED: Cache for 30 seconds (messages change frequently)
            cache.set(cache_key, serialized_data, 30)
            logger.info(f"🚀 Cache MISS: Cached private messages for users {user_ids}")
            
            return Response(serialized_data)
        
        else:
            return Response({"error": "Either receiver_id or group_id must be provided"}, status=status.HTTP_400_BAD_REQUEST)
