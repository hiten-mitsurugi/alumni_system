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

class GroupChatManageView(APIView):
    permission_classes = [IsAuthenticated]
    
    def dispatch(self, request, *args, **kwargs):
        """Override dispatch to debug method handling"""
        logger.info(f"GroupChatManageView dispatch called with method: {request.method}")
        logger.info(f"Available methods: {[method for method in dir(self) if not method.startswith('_') and callable(getattr(self, method))]}")
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, group_id):
        """Get group details including members and admins"""
        logger.info(f"GroupChatManageView GET called for group_id: {group_id} by user: {request.user}")
        
        # Simple test response first
        return Response({
            'test': 'GET method works',
            'group_id': str(group_id),
            'user': str(request.user)
        })
        
        # Original logic commented out for testing
        # try:
        #     group = GroupChat.objects.get(id=group_id)
        #     logger.info(f"Found group: {group.name}")
        #     
        #     if request.user not in group.members.all():
        #         logger.warning(f"User {request.user} is not a member of group {group_id}")
        #         return Response({'error': 'Not a member of this group'}, status=status.HTTP_403_FORBIDDEN)
        #     
        #     logger.info(f"User {request.user} is a member, serializing group data")
        #     serializer = GroupChatSerializer(group, context={'request': request})
        #     logger.info(f"Serialized data: {serializer.data}")
        #     return Response(serializer.data)
        # except GroupChat.DoesNotExist:
        #     logger.error(f"Group {group_id} not found")
        #     return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)
        # except Exception as e:
        #     logger.error(f"Error in GroupChatManageView GET: {str(e)}")
        #     return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request, group_id):
        logger.info(f"GroupChatManageView POST called with group_id: {group_id}")
        logger.info(f"Request user: {request.user}")
        logger.info(f"Request data: {request.data}")
        
        try:
            group = GroupChat.objects.get(id=group_id)
            logger.info(f"Found group: {group.name}")
            
            action = request.data.get('action')
            logger.info(f"Action requested: {action}")
            
            # Handle leave_group action first (any member can leave)
            if action == 'leave_group':
                logger.info("Processing leave_group action")
                
                # Check if user is a member
                if request.user not in group.members.all():
                    logger.warning(f"User {request.user.id} tried to leave group {group_id} but is not a member")
                    return Response({'error': 'Not a member of this group'}, status=status.HTTP_403_FORBIDDEN)
                
                logger.info(f"User {request.user.id} is leaving group {group_id}")
                
                try:
                    # Create system message for user leaving
                    try:
                        from ..models import Message
                        system_message = Message.objects.create(
                            group=group,
                            sender=request.user,  # Use the leaving user as sender
                            content=f"{request.user.first_name} {request.user.last_name} left the group"
                        )
                        logger.info(f"Created system message for user leaving: {system_message.id}")
                    except Exception as e:
                        logger.error(f"Error creating leave system message: {e}")
                        # Don't let this error stop the leave action
                    
                    # Remove user from members and admins
                    group.members.remove(request.user)
                    if request.user in group.admins.all():
                        group.admins.remove(request.user)
                        logger.info("User was also removed from admins")
                    
                    # Send real-time notification to all remaining group members
                    try:
                        from channels.layers import get_channel_layer
                        from asgiref.sync import async_to_sync
                        
                        channel_layer = get_channel_layer()
                        
                        # Send notification to all remaining members about the system message
                        for member in group.members.all():
                            async_to_sync(channel_layer.group_send)(f'user_{member.id}', {
                                'type': 'group_member_left',
                                'group_id': group.id,
                                'group_name': group.name,
                                'left_user': {
                                    'id': request.user.id,
                                    'first_name': request.user.first_name,
                                    'last_name': request.user.last_name
                                },
                                'system_message': {
                                    'id': system_message.id if 'system_message' in locals() else None,
                                    'content': f"{request.user.first_name} {request.user.last_name} left the group",
                                    'timestamp': system_message.timestamp.isoformat() if 'system_message' in locals() else None
                                }
                            })
                        
                        # Send notification to the user who left (to remove group from their list)
                        async_to_sync(channel_layer.group_send)(f'user_{request.user.id}', {
                            'type': 'group_member_left',
                            'group_id': group.id,
                            'group_name': group.name,
                            'user_left_group': True  # Special flag for the user who left
                        })
                        
                        logger.info(f"Sent leave group notifications to all members")
                        
                    except Exception as e:
                        logger.error(f"Error sending leave group notification: {e}")
                        # Don't let this error affect the main functionality
                    
                    logger.info(f"User {request.user.id} successfully left group {group_id}")
                    return Response({'message': 'Left group successfully', 'success': True})
                    
                except Exception as e:
                    logger.error(f"Error removing user from group: {e}")
                    return Response({'error': f'Failed to leave group: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # For all other actions, check if user is member and admin
            if request.user not in group.members.all():
                return Response({'error': 'Not a member of this group'}, status=status.HTTP_403_FORBIDDEN)
                
            if request.user not in group.admins.all():
                return Response({'error': 'Not an admin'}, status=status.HTTP_403_FORBIDDEN)
            
            user_id = request.data.get('user_id')
            
            if action == 'add_member':
                from django.contrib.auth import get_user_model
                User = get_user_model()
                
                try:
                    new_member = User.objects.get(id=user_id)
                    
                    # Check if user is already a member
                    if new_member in group.members.all():
                        return Response({'error': 'User is already a member of this group'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    # Add the new member
                    group.members.add(new_member)
                    
                    # Create system message for member addition
                    try:
                        from ..models import Message
                        system_message = Message.objects.create(
                            group=group,
                            sender=request.user,  # Use the admin who added as sender
                            content=f"{new_member.first_name} {new_member.last_name} was added to the group by {request.user.first_name} {request.user.last_name}"
                        )
                        logger.info(f"Created system message for member addition: {system_message.id}")
                    except Exception as e:
                        logger.error(f"Error creating add member system message: {e}")
                        # Don't let this error stop the add action
                    
                    # Send real-time notifications
                    try:
                        from channels.layers import get_channel_layer
                        from asgiref.sync import async_to_sync
                        
                        channel_layer = get_channel_layer()
                        group_serializer = GroupChatSerializer(group, context={'request': request})
                        
                        # Send notification to the newly added user to show the group in their conversation list
                        async_to_sync(channel_layer.group_send)(f'user_{new_member.id}', {
                            'type': 'group_created',
                            'group': group_serializer.data,
                            'creator': {
                                'id': request.user.id,
                                'first_name': request.user.first_name,
                                'last_name': request.user.last_name
                            }
                        })
                        
                        # Send notification to all existing members about the system message
                        for member in group.members.all():
                            if member.id != new_member.id:  # Don't send to the newly added member
                                async_to_sync(channel_layer.group_send)(f'user_{member.id}', {
                                    'type': 'group_member_added',
                                    'group_id': group.id,
                                    'group_name': group.name,
                                    'added_user': {
                                        'id': new_member.id,
                                        'first_name': new_member.first_name,
                                        'last_name': new_member.last_name
                                    },
                                    'added_by': {
                                        'id': request.user.id,
                                        'first_name': request.user.first_name,
                                        'last_name': request.user.last_name
                                    },
                                    'system_message': {
                                        'id': system_message.id if 'system_message' in locals() else None,
                                        'content': f"{new_member.first_name} {new_member.last_name} was added to the group by {request.user.first_name} {request.user.last_name}",
                                        'timestamp': system_message.timestamp.isoformat() if 'system_message' in locals() else None
                                    }
                                })
                        
                        logger.info(f"Sent group added notification to newly added user {new_member.id} and system message to existing members")
                        
                    except Exception as e:
                        logger.error(f"Error sending group added notification: {e}")
                        # Don't let this error affect the main functionality
                    
                    # Return success response for add_member
                    return Response({
                        'message': 'Member added successfully',
                        'success': True
                    })
                        
                except User.DoesNotExist:
                    return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
                    
            elif action == 'remove_member':
                from django.contrib.auth import get_user_model
                User = get_user_model()
                
                try:
                    member_to_remove = User.objects.get(id=user_id)
                    
                    # Check if user is actually a member
                    if member_to_remove not in group.members.all():
                        return Response({'error': 'User is not a member of this group'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    # Remove the member
                    group.members.remove(member_to_remove)
                    
                    # Also remove from admins if they were an admin
                    if member_to_remove in group.admins.all():
                        group.admins.remove(member_to_remove)
                    
                    # Create system message for member removal
                    try:
                        from ..models import Message
                        system_message = Message.objects.create(
                            group=group,
                            sender=request.user,  # Use the admin who removed as sender
                            content=f"{member_to_remove.first_name} {member_to_remove.last_name} was removed from the group by {request.user.first_name} {request.user.last_name}"
                        )
                        logger.info(f"Created system message for member removal: {system_message.id}")
                    except Exception as e:
                        logger.error(f"Error creating remove member system message: {e}")
                        # Don't let this error stop the remove action
                    
                    # Send real-time notifications
                    try:
                        from channels.layers import get_channel_layer
                        from asgiref.sync import async_to_sync
                        
                        channel_layer = get_channel_layer()
                        
                        # Send notification to the removed user to remove the group from their conversation list
                        async_to_sync(channel_layer.group_send)(f'user_{member_to_remove.id}', {
                            'type': 'group_member_left',
                            'group_id': str(group.id),
                            'group_name': group.name,
                            'removed_by': {
                                'id': request.user.id,
                                'first_name': request.user.first_name,
                                'last_name': request.user.last_name
                            }
                        })
                        
                        # Send notification to all remaining members about the system message
                        for member in group.members.all():
                            async_to_sync(channel_layer.group_send)(f'user_{member.id}', {
                                'type': 'group_member_left',
                                'group_id': group.id,
                                'group_name': group.name,
                                'removed_user': {
                                    'id': member_to_remove.id,
                                    'first_name': member_to_remove.first_name,
                                    'last_name': member_to_remove.last_name
                                },
                                'removed_by': {
                                    'id': request.user.id,
                                    'first_name': request.user.first_name,
                                    'last_name': request.user.last_name
                                },
                                'system_message': {
                                    'id': system_message.id if 'system_message' in locals() else None,
                                    'content': f"{member_to_remove.first_name} {member_to_remove.last_name} was removed from the group by {request.user.first_name} {request.user.last_name}",
                                    'timestamp': system_message.timestamp.isoformat() if 'system_message' in locals() else None
                                }
                            })
                        
                        logger.info(f"Sent group removal notification to removed user {member_to_remove.id} and system message to remaining members")
                        
                    except Exception as e:
                        logger.error(f"Error sending group removal notification: {e}")
                        # Don't let this error affect the main functionality
                    
                    # Return success response for remove_member (same pattern as add_member)
                    return Response({
                        'message': 'Member removed successfully',
                        'success': True
                    })
                        
                except User.DoesNotExist:
                    return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            elif action == 'promote_admin':
                group.admins.add(user_id)
            elif action == 'demote_admin':
                group.admins.remove(user_id)
            elif action == 'update_picture':
                # Handle group picture update
                group_picture = request.FILES.get('group_picture')
                if group_picture:
                    # Delete old picture if it exists
                    if group.group_picture:
                        try:
                            group.group_picture.delete(save=False)
                        except Exception as e:
                            logger.warning(f"Could not delete old group picture: {e}")
                    
                    group.group_picture = group_picture
                    group.save()
                    logger.info(f"Group picture updated for group {group_id}")
                else:
                    return Response({'error': 'No image file provided'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = GroupChatSerializer(group, context={'request': request})
            return Response(serializer.data)
            
        except GroupChat.DoesNotExist:
            return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in GroupChatManageView POST: {e}")
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
