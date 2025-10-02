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

class BumpMessageView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, message_id):
        """
        Bump a message - creates a new message that references the original.
        Like Facebook Messenger's bump feature.
        """
        try:
            # Get the original message - must be sender's own message
            original_message = get_object_or_404(
                Message, 
                id=message_id, 
                sender=request.user
            )
            
            # Determine the receiver based on original message type
            if original_message.receiver:
                # Private message - bump to same receiver
                receiver = original_message.receiver
                group = None
            elif original_message.group:
                # Group message - bump to same group
                receiver = None
                group = original_message.group
                
                # Check if user is still a member of the group
                if request.user not in group.members.all():
                    return Response({
                        'error': 'You are no longer a member of this group'
                    }, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({
                    'error': 'Invalid message type'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create the bump message
            bump_message = Message.objects.create(
                sender=request.user,
                receiver=receiver,
                group=group,
                content=f"🔔 Bumped message",  # Special content indicating this is a bump
                reply_to=original_message  # Reference to original message
            )
            
            # Serialize the new bump message with full relationships
            bump_message_with_relations = Message.objects.select_related(
                'sender', 'receiver', 'group', 'reply_to', 'reply_to__sender'
            ).prefetch_related('attachments').get(id=bump_message.id)
            
            serializer = MessageSerializer(
                bump_message_with_relations, 
                context={'request': request}
            )
            
            # Send real-time notification via WebSocket
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            
            channel_layer = get_channel_layer()
            
            if receiver:
                # Private message bump - notify receiver
                async_to_sync(channel_layer.group_send)(
                    f'user_{receiver.id}',
                    {
                        'type': 'chat_message',
                        'message': serializer.data
                    }
                )
                # Also notify sender for real-time update
                async_to_sync(channel_layer.group_send)(
                    f'user_{request.user.id}',
                    {
                        'type': 'chat_message',
                        'message': serializer.data
                    }
                )
            elif group:
                # Group message bump - notify all group members
                async_to_sync(channel_layer.group_send)(
                    f'group_{group.id}',
                    {
                        'type': 'chat_message',
                        'message': serializer.data
                    }
                )
            
            return Response({
                'status': 'Message bumped successfully',
                'message': serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error bumping message {message_id}: {e}")
            return Response({
                'error': 'Failed to bump message'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
