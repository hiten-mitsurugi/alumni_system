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

class UnreadCountsView(APIView):
    """Get unread message and message request counts for the current user with Redis caching"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Return unread counts for messages and message requests"""
        try:
            user = request.user
            
            # 🚀 SPEED: Try to get cached unread counts first
            cache_key = f"unread_counts_{user.id}"
            cached_counts = cache.get(cache_key)
            
            if cached_counts:
                logger.info(f"🚀 Cache HIT: Returning cached unread counts for user {user.id}")
                return Response(cached_counts)
            
            logger.info(f"🚀 Cache MISS: Calculating unread counts for user {user.id}")
            
            # Count unread private messages
            # Messages where user is receiver and message is not read
            unread_private_messages = Message.objects.filter(
                receiver=user,
                is_read=False
            ).count()
            
            # Count unread group messages
            # Messages in groups where user is member but hasn't read the message
            user_groups = GroupChat.objects.filter(members=user)
            unread_group_messages = 0
            
            for group in user_groups:
                # Get messages in this group from other users that this user hasn't read
                group_messages = Message.objects.filter(
                    group=group
                ).exclude(sender=user)
                
                # Check which messages this user hasn't read
                read_message_ids = MessageRead.objects.filter(
                    user=user,
                    message__group=group
                ).values_list('message_id', flat=True)
                
                unread_in_group = group_messages.exclude(id__in=read_message_ids).count()
                unread_group_messages += unread_in_group
            
            total_unread_messages = unread_private_messages + unread_group_messages
            
            # Count unread message requests
            unread_message_requests = MessageRequest.objects.filter(
                receiver=user,
                accepted=False
            ).count()
            
            logger.info(f"Unread counts for user {user.id}: {total_unread_messages} messages, {unread_message_requests} requests")
            
            # Prepare response data
            response_data = {
                'unread_messages': total_unread_messages,
                'unread_private_messages': unread_private_messages,
                'unread_group_messages': unread_group_messages,
                'unread_message_requests': unread_message_requests,
                'total_unread': total_unread_messages + unread_message_requests
            }
            
            # 🚀 SPEED: Cache for 30 seconds (counts change frequently)
            cache.set(cache_key, response_data, 30)
            logger.info(f"🚀 Cache SET: Cached unread counts for user {user.id}")
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting unread counts for user {request.user.id}: {e}")
            return Response(
                {'error': 'Failed to get unread counts'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
