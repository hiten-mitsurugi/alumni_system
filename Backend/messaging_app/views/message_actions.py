"""
Message action views for pinning, bumping, and forwarding messages.
Handles operations that act on existing messages beyond basic send/read.
"""
import logging
import uuid
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from ..models import Message, GroupChat, BlockedUser
from ..serializers import MessageSerializer

User = get_user_model()
logger = logging.getLogger(__name__)


class PinMessageView(APIView):
    """Pin a message to the top of a conversation"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            message_id = request.data.get('message_id')
            
            if not message_id:
                return Response({
                    'error': 'Message ID is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get the message
            try:
                message = Message.objects.get(id=message_id)
            except Message.DoesNotExist:
                return Response({
                    'error': 'Message not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Check if user has access to pin this message
            has_access = False
            if message.receiver and (request.user == message.sender or request.user == message.receiver):
                has_access = True
            elif message.group and request.user in message.group.members.all():
                has_access = True
            
            if not has_access:
                return Response({
                    'error': 'You do not have access to this message'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Toggle pin status
            message.is_pinned = not message.is_pinned
            message.save()
            
            serializer = MessageSerializer(message, context={'request': request})
            
            return Response({
                'status': f'Message {"pinned" if message.is_pinned else "unpinned"} successfully',
                'message': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error pinning message {message_id}: {e}")
            return Response({
                'error': 'Failed to pin message'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BumpMessageView(APIView):
    """Bump a message to the top (create a duplicate with current timestamp)"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            message_id = request.data.get('message_id')
            
            if not message_id:
                return Response({
                    'error': 'Message ID is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get the original message
            try:
                original_message = Message.objects.get(id=message_id)
            except Message.DoesNotExist:
                return Response({
                    'error': 'Message not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Check if user has access to bump this message
            receiver = original_message.receiver
            group = original_message.group
            
            has_access = False
            if receiver and (request.user == original_message.sender or request.user == receiver):
                has_access = True
            elif group and request.user in group.members.all():
                has_access = True
            
            if not has_access:
                return Response({
                    'error': 'You do not have access to this message'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Create a new message (bump)
            bumped_message = Message.objects.create(
                sender=request.user,
                receiver=receiver,
                group=group,
                content=original_message.content,
                is_bumped=True
            )
            
            # Copy attachments if any
            for attachment in original_message.attachments.all():
                bumped_message.attachments.add(attachment)
            
            serializer = MessageSerializer(
                bumped_message,
                context={'request': request}
            )
            
            # Send real-time notification via WebSocket
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
