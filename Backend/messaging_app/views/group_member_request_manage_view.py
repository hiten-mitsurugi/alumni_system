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
