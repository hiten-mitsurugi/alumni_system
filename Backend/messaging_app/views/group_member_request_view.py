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
    
    def get(self, request, group_id):
        """Get pending member requests for a group (admin only)"""
        try:
            group = GroupChat.objects.get(id=group_id)
            
            # Check if user is admin
            if request.user not in group.admins.all():
                return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
            
            pending_requests = GroupMemberRequest.objects.filter(
                group=group,
                status='pending'
            ).order_by('-created_at')
            
            serializer = GroupMemberRequestSerializer(pending_requests, many=True)
            return Response(serializer.data)
            
        except GroupChat.DoesNotExist:
            return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)
