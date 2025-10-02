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

class ForwardMessageView(APIView):
    """Forward a message to one or more conversations (private or group)"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            message_id = request.data.get('message_id')
            destinations = request.data.get('destinations', [])  # Array of {type: 'private'/'group', id: 'user_id'/'group_id'}
            
            if not message_id or not destinations:
                return Response({
                    'error': 'Message ID and destinations are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get the original message
            try:
                original_message = Message.objects.get(id=message_id)
            except Message.DoesNotExist:
                return Response({
                    'error': 'Original message not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Check if user has access to the original message
            has_access = False
            if original_message.receiver == request.user or original_message.sender == request.user:
                has_access = True
            elif original_message.group and request.user in original_message.group.members.all():
                has_access = True
                
            if not has_access:
                return Response({
                    'error': 'You do not have access to this message'
                }, status=status.HTTP_403_FORBIDDEN)
            
            forwarded_messages = []
            
            # Helper to make serializer JSON-safe for UUIDs
            def serialize_message_json_safe(message_obj):
                data = MessageSerializer(message_obj, context={'request': request}).data
                # Ensure UUID fields are strings
                if isinstance(data.get('id'), uuid.UUID):
                    data['id'] = str(data['id'])
                # Receiver and sender ids are already primitives via UserSearchSerializer
                # Group may be UUID in nested structures; ensure it is string if present
                if isinstance(data.get('group'), uuid.UUID):
                    data['group'] = str(data['group'])
                # Reply and forwarded_from handled in serializer as strings
                # Attachments ids are strings by serializer
                return data
            
            # Process each destination
            for destination in destinations:
                dest_type = destination.get('type')
                dest_id = destination.get('id')
                
                if dest_type == 'private':
                    # Forward to private conversation
                    try:
                        receiver = User.objects.get(id=dest_id)
                        
                        # Check if sender is blocked by receiver
                        is_blocked = BlockedUser.objects.filter(
                            user=receiver, 
                            blocked_user=request.user
                        ).exists()
                        
                        if is_blocked:
                            continue  # Skip this destination if blocked
                        
                        # Create forwarded message
                        forwarded_message = Message.objects.create(
                            sender=request.user,
                            receiver=receiver,
                            content=original_message.content,
                            is_forwarded=True,
                            forwarded_from=original_message
                        )
                        
                        # Copy attachments from original message
                        for attachment in original_message.attachments.all():
                            forwarded_message.attachments.add(attachment)
                        
                        forwarded_messages.append(forwarded_message)
                        
                        # Send real-time notification via WebSocket
                        from channels.layers import get_channel_layer
                        from asgiref.sync import async_to_sync
                        
                        channel_layer = get_channel_layer()
                        serializer_data = serialize_message_json_safe(forwarded_message)
                        
                        # Notify receiver
                        async_to_sync(channel_layer.group_send)(
                            f'user_{receiver.id}',
                            {
                                'type': 'chat_message',
                                'message': serializer_data
                            }
                        )
                        
                        # Notify sender
                        async_to_sync(channel_layer.group_send)(
                            f'user_{request.user.id}',
                            {
                                'type': 'chat_message',
                                'message': serializer_data
                            }
                        )
                        
                    except User.DoesNotExist:
                        continue  # Skip invalid user
                
                elif dest_type == 'group':
                    # Forward to group conversation
                    try:
                        group = GroupChat.objects.get(id=dest_id)
                        
                        # Check if user is a member of the group
                        if request.user not in group.members.all():
                            continue  # Skip if not a member
                        
                        # Create forwarded message
                        forwarded_message = Message.objects.create(
                            sender=request.user,
                            group=group,
                            content=original_message.content,
                            is_forwarded=True,
                            forwarded_from=original_message
                        )
                        
                        # Copy attachments from original message
                        for attachment in original_message.attachments.all():
                            forwarded_message.attachments.add(attachment)
                        
                        forwarded_messages.append(forwarded_message)
                        
                        # Send real-time notification via WebSocket
                        from channels.layers import get_channel_layer
                        from asgiref.sync import async_to_sync
                        
                        channel_layer = get_channel_layer()
                        serializer_data = serialize_message_json_safe(forwarded_message)
                        
                        # Notify all group members
                        async_to_sync(channel_layer.group_send)(
                            f'group_{group.id}',
                            {
                                'type': 'chat_message',
                                'message': serializer_data
                            }
                        )
                        
                    except GroupChat.DoesNotExist:
                        continue  # Skip invalid group
            
            return Response({
                'status': f'Message forwarded to {len(forwarded_messages)} destination(s)',
                'forwarded_count': len(forwarded_messages)
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error forwarding message: {e}")
            return Response({
                'error': 'Failed to forward message'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
