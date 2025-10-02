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

class MessageRequestView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        requests = MessageRequest.objects.filter(receiver=request.user, accepted=False)
        serializer = MessageRequestSerializer(requests, many=True)
        return Response(serializer.data)
    def post(self, request):
        action = request.data.get('action')
        request_id = request.data.get('request_id')
        msg_request = MessageRequest.objects.get(id=request_id, receiver=request.user)
        if action == 'accept':
            msg_request.accepted = True
            msg_request.save()
            # Create a message with the original content from the request
            message = Message.objects.create(
                sender=msg_request.sender,
                receiver=request.user,
                content=msg_request.content  # Use the actual message content
            )
            
            # Invalidate cache for both users (accepting request affects unread counts)
            invalidate_unread_counts_cache(msg_request.sender.id)
            invalidate_unread_counts_cache(request.user.id)
            
            # Send real-time notification to sender that request was accepted
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'user_{msg_request.sender.id}',
                {
                    'type': 'request_accepted',
                    'message': {
                        'id': str(message.id),
                        'content': message.content,
                        'receiver': {'id': request.user.id, 'first_name': request.user.first_name},
                        'timestamp': message.timestamp.isoformat()
                    }
                }
            )
            
            return Response({'status': 'Request accepted', 'message_id': str(message.id)})
        elif action == 'decline':
            # Invalidate cache for receiver (declining request affects unread counts)
            invalidate_unread_counts_cache(request.user.id)
            
            msg_request.delete()
            return Response({'status': 'Request declined'})
        return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
