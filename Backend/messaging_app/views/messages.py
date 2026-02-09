"""
Message sending and listing views for messaging app.
Handles sending messages and retrieving message lists.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Q
from django.utils import timezone
from django.core.cache import cache
from django.contrib.auth import get_user_model
import logging

from ..models import Message, MessageRequest, BlockedUser, GroupChat, Attachment
from ..serializers import MessageSerializer
from ..link_utils import create_link_previews_for_message
from .cache_utils import invalidate_unread_counts_cache

logger = logging.getLogger(__name__)
User = get_user_model()


class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        receiver_id = request.data.get('receiver_id')
        content = request.data.get('content')
        reply_to_id = request.data.get('reply_to_id')
        attachment_ids = request.data.get('attachment_ids', [])

        if not receiver_id or not content:
            return Response({'error': 'Receiver ID and content required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            receiver = User.objects.get(id=receiver_id)
        except User.DoesNotExist:
            return Response({'error': 'Receiver not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if current user is blocked by receiver
        is_blocked_by_receiver = BlockedUser.objects.filter(
            user=receiver, 
            blocked_user=request.user
        ).exists()
        
        if is_blocked_by_receiver:
            return Response({
                'error': 'You cannot send messages to this user. You have been blocked.'
            }, status=status.HTTP_403_FORBIDDEN)

        # Check if current user has blocked the receiver
        has_blocked_receiver = BlockedUser.objects.filter(
            user=request.user, 
            blocked_user=receiver
        ).exists()
        
        if has_blocked_receiver:
            return Response({
                'error': 'You cannot send messages to a user you have blocked. Please unblock them first.'
            }, status=status.HTTP_403_FORBIDDEN)

        # Check if there's an existing conversation (either messages exist OR accepted message requests exist)
        has_conversation = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=receiver)) |
            (Q(sender=receiver) & Q(receiver=request.user))
        ).exists() or MessageRequest.objects.filter(
            (Q(sender=request.user) & Q(receiver=receiver)) |
            (Q(sender=receiver) & Q(receiver=request.user)),
            accepted=True
        ).exists()

        if not has_conversation:
            # Create a message request if no prior conversation
            message_request = MessageRequest.objects.create(
                sender=request.user,
                receiver=receiver,
                content=content,
                timestamp=timezone.now()
            )
            
            # 🚀 NEW: Invalidate unread counts cache for receiver
            invalidate_unread_counts_cache(receiver.id)
            
            return Response({
                'status': 'Message request sent',
                'request_id': str(message_request.id)
            }, status=status.HTTP_201_CREATED)
        else:
            # Create message if conversation exists
            message = Message.objects.create(
                sender=request.user,
                receiver=receiver,
                content=content
            )
            
            # Add reply_to if provided
            if reply_to_id:
                try:
                    reply_message = Message.objects.get(id=reply_to_id)
                    message.reply_to = reply_message
                    message.save()
                except Message.DoesNotExist:
                    pass
            
            # Add attachments
            for attachment_id in attachment_ids:
                try:
                    attachment = Attachment.objects.get(id=attachment_id)
                    message.attachments.add(attachment)
                except Attachment.DoesNotExist:
                    pass
            
            # Generate link previews automatically
            try:
                create_link_previews_for_message(message)
            except Exception as e:
                logger.error(f"Failed to create link previews for message {message.id}: {str(e)}")
            
            # 🚀 SPEED: Invalidate caches after sending message
            # Clear conversation caches for both sender and receiver
            cache.delete(f"user_conversations_{request.user.id}")
            cache.delete(f"user_conversations_{receiver.id}")
            
            # Clear message cache for this conversation
            user_ids = sorted([request.user.id, receiver.id])
            cache.delete(f"private_messages_{user_ids[0]}_{user_ids[1]}")
            
            # 🚀 NEW: Invalidate unread counts cache for receiver
            invalidate_unread_counts_cache(receiver.id)
            
            logger.info(f"🚀 Cache invalidated after message sent from {request.user.id} to {receiver.id}")
            
            serializer = MessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


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
                # Defer 'content' field to avoid automatic decryption which may fail with key mismatch
                messages = Message.objects.filter(group=group).select_related(
                    'sender', 'sender__profile', 'reply_to', 'reply_to__sender'
                ).prefetch_related(
                    'attachments', 'reactions', 'reactions__user'
                ).defer('content').order_by("timestamp")
                
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
            # Defer 'content' field to avoid automatic decryption which may fail with key mismatch
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
            ).defer('content').order_by("timestamp")

            serializer = MessageSerializer(messages, many=True, context={'request': request})
            serialized_data = serializer.data
            
            # 🚀 SPEED: Cache for 30 seconds (messages change frequently)
            cache.set(cache_key, serialized_data, 30)
            logger.info(f"🚀 Cache MISS: Cached private messages for users {user_ids}")
            
            return Response(serialized_data)
        
        else:
            return Response({"error": "Either receiver_id or group_id must be provided"}, status=status.HTTP_400_BAD_REQUEST)
