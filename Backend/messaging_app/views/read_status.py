"""
Read status views for marking messages as read and getting unread counts.
Handles message read tracking with Redis caching and WebSocket updates.
"""
import logging
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from ..models import Message, GroupChat, MessageRead, MessageRequest
from ..serializers import MessageSerializer
from .cache_utils import invalidate_unread_counts_cache

User = get_user_model()
logger = logging.getLogger(__name__)


class MarkMessageAsReadView(APIView):
    """Mark a specific message as read and broadcast the update"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, message_id):
        """Mark a message as read by the current user"""
        try:
            # Get the message
            try:
                message = Message.objects.get(id=message_id)
            except Message.DoesNotExist:
                return Response(
                    {'error': 'Message not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            user = request.user
            
            # Check if user has access to this message
            has_access = False
            
            # For private messages
            if message.receiver and (user == message.sender or user == message.receiver):
                has_access = True
                # For private messages, update the is_read field if user is the receiver
                if user == message.receiver and not message.is_read:
                    message.is_read = True
                    message.save()
                    
                    # Send notification update to decrement unread count
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        f'user_{user.id}',
                        {
                            'type': 'notification_update',
                            'data': {
                                'action': 'decrement',
                                'type': 'message',
                                'count': 1
                            }
                        }
                    )
            
            # For group messages
            elif message.group and message.group.members.filter(id=user.id).exists():
                has_access = True
                # For group messages, create MessageRead record if user is not the sender
                if user != message.sender:
                    msg_read_obj, created = MessageRead.objects.get_or_create(
                        message=message,
                        user=user,
                        defaults={'read_at': timezone.now()}
                    )
                    
                    # Send notification update to decrement unread count only if newly created
                    if created:
                        channel_layer = get_channel_layer()
                        async_to_sync(channel_layer.group_send)(
                            f'user_{user.id}',
                            {
                                'type': 'notification_update',
                                'data': {
                                    'action': 'decrement',
                                    'type': 'message',
                                    'count': 1
                                }
                            }
                        )
            
            if not has_access:
                return Response(
                    {'error': 'You do not have access to this message'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Get updated message with read_by information
            updated_message = Message.objects.select_related(
                'sender', 'receiver', 'group'
            ).prefetch_related('read_by__user').get(id=message_id)
            
            # Serialize the message to get the latest read_by data
            serializer = MessageSerializer(updated_message, context={'request': request})
            
            # Broadcast the read status update via WebSocket
            channel_layer = get_channel_layer()
            read_data = {
                'type': 'message_read_update',
                'message_id': str(message.id),
                'user_id': user.id,
                'user_name': f"{user.first_name} {user.last_name}".strip() or user.username,
                'user_profile_picture': serializer.get_profile_picture_url(user),
                'read_at': timezone.now().isoformat(),
                'read_by': serializer.data['read_by'],  # Include full read_by data
                'timestamp': timezone.now().isoformat(),
            }
            
            # Broadcast to private conversation or group
            if message.receiver:
                # Private message - send to both sender and receiver
                for target_user in [message.sender, message.receiver]:
                    async_to_sync(channel_layer.group_send)(
                        f"user_{target_user.id}",
                        read_data
                    )
            elif message.group:
                # Group message - send to all group members
                async_to_sync(channel_layer.group_send)(
                    f"group_{message.group.id}",
                    read_data
                )
            
            # 🚀 NEW: Invalidate unread counts cache when message is marked as read
            invalidate_unread_counts_cache(user.id)
            
            return Response({
                'message': 'Message marked as read successfully',
                'read_by': serializer.data['read_by']
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error marking message as read {message_id}: {e}")
            return Response(
                {'error': 'Failed to mark message as read'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UnreadCountsView(APIView):
    """Get unread message and message request counts for the current user with Redis caching"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Return unread counts for messages and message requests"""
        try:
            user = request.user
            
            # 🚀 SPEED: Try to get cached unread counts first
            cache_key = f"unread_counts_{user.id}"
            cached_counts = cache.get(cache_key)
            
            if cached_counts:
                logger.info(f"🚀 Cache HIT: Returning cached unread counts for user {user.id}")
                return Response(cached_counts)
            
            logger.info(f"🚀 Cache MISS: Calculating unread counts for user {user.id}")
            
            # Count unread private messages
            # Messages where user is receiver and message is not read
            unread_private_messages = Message.objects.filter(
                receiver=user,
                is_read=False
            ).count()
            
            # Count unread group messages
            # Messages in groups where user is member but hasn't read the message
            user_groups = GroupChat.objects.filter(members=user)
            unread_group_messages = 0
            
            for group in user_groups:
                # Get messages in this group from other users that this user hasn't read
                group_messages = Message.objects.filter(
                    group=group
                ).exclude(sender=user)
                
                # Check which messages this user hasn't read
                read_message_ids = MessageRead.objects.filter(
                    user=user,
                    message__group=group
                ).values_list('message_id', flat=True)
                
                unread_in_group = group_messages.exclude(id__in=read_message_ids).count()
                unread_group_messages += unread_in_group
            
            total_unread_messages = unread_private_messages + unread_group_messages
            
            # Count unread message requests
            unread_message_requests = MessageRequest.objects.filter(
                receiver=user,
                accepted=False
            ).count()
            
            logger.info(f"Unread counts for user {user.id}: {total_unread_messages} messages, {unread_message_requests} requests")
            
            # Prepare response data
            response_data = {
                'unread_messages': total_unread_messages,
                'unread_private_messages': unread_private_messages,
                'unread_group_messages': unread_group_messages,
                'unread_message_requests': unread_message_requests,
                'total_unread': total_unread_messages + unread_message_requests
            }
            
            # 🚀 SPEED: Cache for 30 seconds (counts change frequently)
            cache.set(cache_key, response_data, 30)
            logger.info(f"🚀 Cache SET: Cached unread counts for user {user.id}")
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting unread counts for user {request.user.id}: {e}")
            return Response(
                {'error': 'Failed to get unread counts'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
