"""
Message request and group member request views for messaging app.
Handles accepting/declining message requests and managing group member requests.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth import get_user_model
import logging

from ..models import Message, MessageRequest, GroupChat, GroupMemberRequest
from ..serializers import MessageRequestSerializer, GroupMemberRequestSerializer
from .cache_utils import invalidate_unread_counts_cache

logger = logging.getLogger(__name__)
User = get_user_model()


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


class GroupMemberRequestView(APIView):
    """Handle group member requests by regular members"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, group_id):
        """Get pending member requests for admins"""
        try:
            group = GroupChat.objects.get(id=group_id)
            
            # Check if user is an admin of the group
            if request.user not in group.admins.all():
                return Response({'error': 'Only admins can view pending requests'}, 
                              status=status.HTTP_403_FORBIDDEN)
            
            # Get all pending requests for this group
            pending_requests = GroupMemberRequest.objects.filter(
                group=group,
                status='pending'
            ).order_by('-created_at')
            
            serializer = GroupMemberRequestSerializer(pending_requests, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except GroupChat.DoesNotExist:
            return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error fetching pending requests: {e}")
            return Response({'error': 'Failed to fetch pending requests'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request, group_id):
        """Request to add a member to the group"""
        try:
            group = GroupChat.objects.get(id=group_id)
            
            # Check if requester is a member of the group
            if request.user not in group.members.all():
                return Response({'error': 'You must be a member to request adding others'}, 
                              status=status.HTTP_403_FORBIDDEN)
            
            user_id = request.data.get('user_id')
            message = request.data.get('message', '')
            
            if not user_id:
                return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                requested_user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Check if user is already a member
            if requested_user in group.members.all():
                return Response({'error': 'User is already a member'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Use get_or_create to handle existing requests properly
            try:
                member_request, created = GroupMemberRequest.objects.get_or_create(
                    group=group,
                    requested_user=requested_user,
                    defaults={
                        'requester': request.user,
                        'message': message,
                        'status': 'pending'
                    }
                )
                
                if not created:
                    # Request already exists, check its status
                    if member_request.status == 'pending':
                        return Response({'error': 'Request already pending for this user'}, 
                                      status=status.HTTP_400_BAD_REQUEST)
                    elif member_request.status == 'approved':
                        return Response({'error': 'User request was already approved'}, 
                                      status=status.HTTP_400_BAD_REQUEST)
                    else:  # rejected - update to new pending request
                        member_request.status = 'pending'
                        member_request.requester = request.user
                        member_request.message = message
                        member_request.admin_response = None
                        member_request.reviewed_by = None
                        member_request.reviewed_at = None
                        member_request.created_at = timezone.now()
                        member_request.save()
                
            except Exception as e:
                logger.error(f"Unexpected error creating member request: {e}")
                return Response({'error': 'Failed to create member request'}, 
                              status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Notify all admins about the new request
            try:
                from channels.layers import get_channel_layer
                from asgiref.sync import async_to_sync
                
                channel_layer = get_channel_layer()
                
                for admin in group.admins.all():
                    async_to_sync(channel_layer.group_send)(
                        f'user_{admin.id}',
                        {
                            'type': 'member_request_notification',
                            'data': {
                                'type': 'member_request',
                                'group_id': str(group.id),
                                'group_name': group.name,
                                'requester': request.user.username,
                                'requested_user': requested_user.username,
                                'message': message,
                                'request_id': str(member_request.id)
                            }
                        }
                    )
            except Exception as e:
                logger.error(f"Error sending member request notification: {e}")
            
            serializer = GroupMemberRequestSerializer(member_request)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except GroupChat.DoesNotExist:
            return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error creating member request: {e}")
            return Response({'error': 'Failed to create request'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GroupMemberRequestManageView(APIView):
    """Handle approval/rejection of member requests by admins"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, request_id):
        """Approve or reject a member request"""
        try:
            member_request = GroupMemberRequest.objects.get(id=request_id)
            group = member_request.group
            
            # Check if user is admin
            if request.user not in group.admins.all():
                return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
            
            action = request.data.get('action')  # 'approve' or 'reject'
            admin_response = request.data.get('admin_response', '')
            
            if action not in ['approve', 'reject']:
                return Response({'error': 'Action must be approve or reject'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            # Update request status
            member_request.status = 'approved' if action == 'approve' else 'rejected'
            member_request.reviewed_by = request.user
            member_request.reviewed_at = timezone.now()
            member_request.admin_response = admin_response
            member_request.save()
            
            # If approved, add user to group
            if action == 'approve':
                group.members.add(member_request.requested_user)
                
                # Notify the requested user they were added
                try:
                    from channels.layers import get_channel_layer
                    from asgiref.sync import async_to_sync
                    
                    channel_layer = get_channel_layer()
                    
                    async_to_sync(channel_layer.group_send)(
                        f'user_{member_request.requested_user.id}',
                        {
                            'type': 'group_added_notification',
                            'data': {
                                'type': 'group_added',
                                'group_id': str(group.id),
                                'group_name': group.name,
                                'approved_by': request.user.username,
                                'message': admin_response
                            }
                        }
                    )
                except Exception as e:
                    logger.error(f"Error sending group added notification: {e}")
            
            # Notify the requester about the decision
            try:
                from channels.layers import get_channel_layer
                from asgiref.sync import async_to_sync
                
                channel_layer = get_channel_layer()
                
                async_to_sync(channel_layer.group_send)(
                    f'user_{member_request.requester.id}',
                    {
                        'type': 'request_response_notification',
                        'data': {
                            'type': 'request_response',
                            'group_id': str(group.id),
                            'group_name': group.name,
                            'requested_user': member_request.requested_user.username,
                            'status': member_request.status,
                            'reviewed_by': request.user.username,
                            'admin_response': admin_response
                        }
                    }
                )
            except Exception as e:
                logger.error(f"Error sending request response notification: {e}")
            
            serializer = GroupMemberRequestSerializer(member_request)
            return Response(serializer.data)
            
        except GroupMemberRequest.DoesNotExist:
            return Response({'error': 'Request not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error managing member request: {e}")
            return Response({'error': 'Failed to process request'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
