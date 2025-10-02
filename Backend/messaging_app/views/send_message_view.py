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

from .cache_utils import invalidate_unread_counts_cache, invalidate_unread_counts_for_users

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
