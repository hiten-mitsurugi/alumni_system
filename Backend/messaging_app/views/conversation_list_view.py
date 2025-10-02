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

class ConversationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.db.models import F, Max, Q
        
        current_user = request.user
        
        # 🚀 SPEED: Try to get cached conversations first
        cache_key = f"user_conversations_{current_user.id}"
        cached_conversations = cache.get(cache_key)
        
        if cached_conversations:
            logger.info(f"🚀 Cache HIT: Returning cached conversations for user {current_user.id}")
            return Response(cached_conversations, status=status.HTTP_200_OK)

        # Get all users blocked by current user (for marking blocked status)
        blocked_user_ids = set(BlockedUser.objects.filter(user=current_user).values_list('blocked_user_id', flat=True))
        
        # Get all users who blocked current user (for marking blocked status)
        blocked_by_user_ids = set(BlockedUser.objects.filter(blocked_user=current_user).values_list('user_id', flat=True))

        # 🚀 SPEED: Optimized query with select_related and prefetch_related
        # Get conversations from both sent and received messages (DO NOT filter out blocked users)
        sent_conversations = Message.objects.filter(
            sender=current_user,
            receiver__isnull=False
        ).values('receiver').annotate(
            other_user_id=F('receiver'),
            last_message_time=Max('timestamp')
        )

        received_conversations = Message.objects.filter(
            receiver=current_user,
            sender__isnull=False
        ).values('sender').annotate(
            other_user_id=F('sender'),
            last_message_time=Max('timestamp')
        )

        # Combine and get unique conversations
        all_conversations = list(sent_conversations) + list(received_conversations)
        
        # Group by other_user_id and get the latest timestamp
        conversation_dict = {}
        for conv in all_conversations:
            user_id = conv['other_user_id']
            if user_id not in conversation_dict or conv['last_message_time'] > conversation_dict[user_id]['last_message_time']:
                conversation_dict[user_id] = conv

        # 🚀 SPEED: Batch fetch all users at once to reduce DB queries
        user_ids = list(conversation_dict.keys())
        users_queryset = User.objects.filter(id__in=user_ids).select_related('profile')
        users_dict = {user.id: user for user in users_queryset}

        # 🚀 SPEED: Batch fetch latest messages for all conversations
        latest_messages_qs = Message.objects.filter(
            Q(sender=current_user, receiver_id__in=user_ids) |
            Q(sender_id__in=user_ids, receiver=current_user)
        ).select_related('sender', 'receiver').order_by('receiver_id', 'sender_id', '-timestamp')
        
        # Group latest messages by conversation
        latest_messages_dict = {}
        for msg in latest_messages_qs:
            # Determine the other user
            other_user_id = msg.receiver_id if msg.sender_id == current_user.id else msg.sender_id
            
            # Only keep the latest message for each conversation
            if other_user_id not in latest_messages_dict:
                latest_messages_dict[other_user_id] = msg

        # 🚀 SPEED: Batch count unread messages for all conversations
        from django.db.models import Count
        unread_counts = Message.objects.filter(
            sender_id__in=user_ids,
            receiver=current_user,
            is_read=False
        ).values('sender_id').annotate(unread_count=Count('id')).values_list('sender_id', 'unread_count')
        unread_dict = {sender_id: count for sender_id, count in unread_counts}

        # Get conversation details for each user
        conversations = []
        for user_id, conv_data in conversation_dict.items():
            if user_id not in users_dict:
                continue
                
            other_user = users_dict[user_id]
            latest_message = latest_messages_dict.get(user_id)

            if latest_message:
                # Build absolute URL for profile picture
                profile_picture_url = None
                if other_user.profile_picture:
                    profile_picture_url = request.build_absolute_uri(other_user.profile_picture.url)
                
                # Check blocking status
                is_blocked_by_me = user_id in blocked_user_ids
                is_blocked_by_them = user_id in blocked_by_user_ids
                
                # Create conversation object
                conversation = {
                    'type': 'private',
                    'mate': {
                        'id': user_id,
                        'username': other_user.username,
                        'first_name': other_user.first_name,
                        'last_name': other_user.last_name,
                        'profile_picture': profile_picture_url,
                        'profile': {
                            'status': getattr(other_user.profile, 'status', 'offline') if hasattr(other_user, 'profile') and other_user.profile else 'offline',
                            'last_seen': getattr(other_user.profile, 'last_seen', None) if hasattr(other_user, 'profile') and other_user.profile else None,
                        }
                    },
                    'lastMessage': latest_message.content[:50] + ('...' if len(latest_message.content) > 50 else ''),
                    'timestamp': latest_message.timestamp.isoformat(),
                    'unreadCount': unread_dict.get(user_id, 0),
                    'isBlockedByMe': is_blocked_by_me,
                    'isBlockedByThem': is_blocked_by_them,
                    'canSendMessage': not (is_blocked_by_me or is_blocked_by_them)
                }
                conversations.append(conversation)

        # Sort by timestamp (newest first)
        conversations.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # 🚀 SPEED: Cache for 10 seconds (conversations change frequently)
        cache.set(cache_key, conversations, 10)
        logger.info(f"🚀 Cache MISS: Cached conversations for user {current_user.id}")

        return Response(conversations, status=status.HTTP_200_OK)
