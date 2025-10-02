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

class MessageReactionsListView(APIView):
    """Get all reactions for a specific message"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, message_id):
        """Get all reactions for a message"""
        try:
            # Get the message
            try:
                message = Message.objects.get(id=message_id)
            except Message.DoesNotExist:
                return Response(
                    {'error': 'Message not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Check if user has access to this message
            user = request.user
            has_access = False
            
            # For private messages
            if message.receiver and (user == message.sender or user == message.receiver):
                has_access = True
            
            # For group messages
            elif message.group and message.group.members.filter(id=user.id).exists():
                has_access = True
            
            if not has_access:
                return Response(
                    {'error': 'You do not have access to this message'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Get reaction statistics
            reaction_view = MessageReactionView()
            reaction_stats = reaction_view.get_reaction_stats(message)
            
            return Response(reaction_stats, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in MessageReactionsListView: {e}")
            return Response(
                {'error': 'Failed to get message reactions'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
