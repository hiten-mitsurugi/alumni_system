"""
Conversation-related views for messaging app.
Handles conversation listing and user conversation queries.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Q, F, Max, Count
from django.core.cache import cache
from django.conf import settings
import logging

from ..models import Message, MessageRequest, BlockedUser, GroupChat, MessageRead
from ..serializers import UserSearchSerializer, MessageSerializer
from .cache_utils import invalidate_unread_counts_cache

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
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user_ids = list(conversation_dict.keys())
        users_queryset = User.objects.filter(id__in=user_ids).select_related('profile')
        users_dict = {user.id: user for user in users_queryset}

        # 🚀 SPEED: Batch fetch latest messages for all conversations
        # Defer 'content' field to avoid automatic decryption which may fail with key mismatch
        latest_messages_qs = Message.objects.filter(
            Q(sender=current_user, receiver_id__in=user_ids) |
            Q(sender_id__in=user_ids, receiver=current_user)
        ).select_related('sender', 'receiver').defer('content').order_by('receiver_id', 'sender_id', '-timestamp')
        
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

            # Build absolute URL for profile picture
            profile_picture_url = None
            if other_user.profile_picture:
                profile_picture_url = request.build_absolute_uri(other_user.profile_picture.url)
            
            # Check blocking status
            is_blocked_by_me = user_id in blocked_user_ids
            is_blocked_by_them = user_id in blocked_by_user_ids
            
            # Try to get message content and timestamp
            if latest_message:
                try:
                    last_message_text = latest_message.content[:50] + ('...' if len(latest_message.content) > 50 else '')
                except Exception:
                    # Encryption error - message exists but can't be decrypted
                    last_message_text = '[Message content unavailable]'
                timestamp = latest_message.timestamp.isoformat()
            else:
                # No latest message available (possibly due to encryption error)
                last_message_text = '[Message content unavailable]'
                timestamp = conv_data['last_message_time'].isoformat()
            
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
                'lastMessage': last_message_text,
                'timestamp': timestamp,
                'unreadCount': unread_dict.get(user_id, 0),
                'isBlockedByMe': is_blocked_by_me,
                'isBlockedByThem': is_blocked_by_them,
                'canSendMessage': not (is_blocked_by_me or is_blocked_by_them)
            }
            conversations.append(conversation)

        # 🆕 ADDITION: Include pending message requests sent by current user
        # This allows users to see their outgoing messages immediately, even if not yet accepted
        # Defer 'content' field to avoid automatic decryption which may fail with key mismatch
        pending_requests = MessageRequest.objects.filter(
            sender=current_user,
            accepted=False
        ).exclude(
            receiver_id__in=conversation_dict.keys()  # Don't duplicate existing conversations
        ).select_related('receiver', 'receiver__profile').defer('content')
        
        for msg_request in pending_requests:
            receiver = msg_request.receiver
            
            # Skip if receiver is blocked
            is_blocked_by_me = receiver.id in blocked_user_ids
            is_blocked_by_them = receiver.id in blocked_by_user_ids
            
            # Build profile picture URL
            profile_picture_url = None
            if receiver.profile_picture:
                profile_picture_url = request.build_absolute_uri(receiver.profile_picture.url)
            
            # Try to get message content, handle encryption errors
            try:
                pending_message_text = f"[Pending] {msg_request.content[:50]}" + ('...' if len(msg_request.content) > 50 else '')
            except Exception:
                pending_message_text = '[Pending message - content unavailable]'
            
            # Create conversation object for pending request
            conversation = {
                'type': 'private',
                'mate': {
                    'id': receiver.id,
                    'username': receiver.username,
                    'first_name': receiver.first_name,
                    'last_name': receiver.last_name,
                    'profile_picture': profile_picture_url,
                    'profile': {
                        'status': getattr(receiver.profile, 'status', 'offline') if hasattr(receiver, 'profile') and receiver.profile else 'offline',
                        'last_seen': getattr(receiver.profile, 'last_seen', None) if hasattr(receiver, 'profile') and receiver.profile else None,
                    }
                },
                'lastMessage': pending_message_text,
                'timestamp': msg_request.timestamp.isoformat(),
                'unreadCount': 0,  # No unread count for pending requests
                'isBlockedByMe': is_blocked_by_me,
                'isBlockedByThem': is_blocked_by_them,
                'canSendMessage': not (is_blocked_by_me or is_blocked_by_them),
                'isPending': True,  # Flag to indicate this is a pending request
                'requestId': str(msg_request.id)
            }
            conversations.append(conversation)

        # Sort by timestamp (newest first)
        conversations.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # 🚀 SPEED: Cache for 10 seconds (conversations change frequently)
        cache.set(cache_key, conversations, 10)
        logger.info(f"🚀 Cache MISS: Cached conversations for user {current_user.id}")

        return Response(conversations, status=status.HTTP_200_OK)


class ConversationUsersView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = request.user
        users = User.objects.filter(
            Q(sent_messages__receiver=user) | Q(received_messages__sender=user)
        ).distinct()
        serializer = UserSearchSerializer(users, many=True, context={'request': request})
        return Response(serializer.data)
