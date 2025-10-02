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

class PinMessageView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, message_id):
        """Pin or unpin a message"""
        try:
            message = get_object_or_404(Message, id=message_id)
            
            # Check if user has permission to pin this message
            # For private messages: either sender or receiver can pin
            # For group messages: any group member can pin
            can_pin = False
            
            if message.receiver:  # Private message
                if request.user == message.sender or request.user == message.receiver:
                    can_pin = True
            elif message.group:  # Group message
                if request.user in message.group.members.all():
                    can_pin = True
            
            if not can_pin:
                return Response({
                    'error': 'You do not have permission to pin this message'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Toggle pin status
            message.is_pinned = not message.is_pinned
            message.save()
            
            # Send real-time notification via WebSocket
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            
            channel_layer = get_channel_layer()
            
            # Prepare message data for WebSocket
            serializer = MessageSerializer(message, context={'request': request})
            
            if message.receiver:  # Private message
                # Notify both sender and receiver
                for user_id in [message.sender.id, message.receiver.id]:
                    async_to_sync(channel_layer.group_send)(
                        f'user_{user_id}',
                        {
                            'type': 'message_pinned',
                            'message': serializer.data,
                            'action': 'pin' if message.is_pinned else 'unpin'
                        }
                    )
            elif message.group:  # Group message
                # Notify all group members
                async_to_sync(channel_layer.group_send)(
                    f'group_{message.group.id}',
                    {
                        'type': 'message_pinned',
                        'message': serializer.data,
                        'action': 'pin' if message.is_pinned else 'unpin'
                    }
                )
            
            return Response({
                'status': f'Message {"pinned" if message.is_pinned else "unpinned"} successfully',
                'message': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error pinning/unpinning message {message_id}: {e}")
            return Response({
                'error': 'Failed to pin/unpin message'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
