"""
Group chat management views for messaging app.
Handles group creation, management, member operations, and group listing.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Q
from django.core.cache import cache
from django.contrib.auth import get_user_model
import logging
import json

from ..models import Message, GroupChat, MessageRead
from ..serializers import GroupChatSerializer

logger = logging.getLogger(__name__)
User = get_user_model()


class GroupChatCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        print(f"DEBUG: request.data = {request.data}")
        print(f"DEBUG: request.FILES = {request.FILES}")
        print(f"DEBUG: Content-Type = {request.content_type}")
        
        name = request.data.get('name')
        description = request.data.get('description', '')
        members_data = request.data.get('members', [])
        group_picture = request.FILES.get('group_picture')
        
        print(f"DEBUG: name = {name}")
        print(f"DEBUG: members_data = {members_data}, type = {type(members_data)}")
        print(f"DEBUG: group_picture = {group_picture}")
        
        # Handle both JSON array and JSON string formats
        if isinstance(members_data, str):
            try:
                member_ids = json.loads(members_data)
                print(f"DEBUG: Parsed member_ids from string = {member_ids}")
            except (json.JSONDecodeError, TypeError) as e:
                print(f"DEBUG: JSON parsing error = {e}")
                return Response({'error': f'Invalid members format: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            member_ids = members_data
            print(f"DEBUG: Using members_data as-is = {member_ids}")
        
        if not name or not member_ids:
            return Response({'error': 'Name and members required'}, status=status.HTTP_400_BAD_REQUEST)
            
        if len(name.strip()) < 1:
            return Response({'error': 'Group name cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)
            
        if len(member_ids) < 1:
            return Response({'error': 'At least one member is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get valid members (exclude current user from member_ids, we'll add them separately)
            valid_members = User.objects.filter(id__in=member_ids).exclude(id=request.user.id)
            
            # Create the group
            group = GroupChat.objects.create(
                name=name.strip(),
                description=description.strip() if description else None,
                group_picture=group_picture
            )
            
            # Add creator and selected members
            group.members.add(request.user, *valid_members)
            # Make creator an admin
            group.admins.add(request.user)
            
            # Serialize with proper context for URL building
            serializer = GroupChatSerializer(group, context={'request': request})
            
            # Send real-time notification to added members
            try:
                from channels.layers import get_channel_layer
                from asgiref.sync import async_to_sync
                
                channel_layer = get_channel_layer()
                
                for member in valid_members:
                    try:
                        async_to_sync(channel_layer.group_send)(
                            f'user_{member.id}',
                            {
                                'type': 'group_created',
                                'group': serializer.data,
                                'creator': {
                                    'id': request.user.id,
                                    'first_name': request.user.first_name,
                                    'last_name': request.user.last_name
                                },
                                'message': f'You were added to "{name}" by {request.user.first_name} {request.user.last_name}'
                            }
                        )
                    except Exception as notification_error:
                        logger.error(f"Failed to send notification to user {member.id}: {str(notification_error)}")
                        # Continue with other notifications even if one fails
                        
            except Exception as e:
                logger.error(f"Failed to send group creation notifications: {str(e)}")
                # Don't fail the entire request if notifications fail
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creating group: {str(e)}")
            return Response({'error': 'Failed to create group'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
                try:
                    new_member = User.objects.get(id=user_id)
                    
                    # Check if user is already a member
                    if new_member in group.members.all():
                        return Response({'error': 'User is already a member of this group'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    # Add the new member
                    group.members.add(new_member)
                    
                    # Create system message for member addition
                    try:
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


class GroupMembersView(APIView):
    """Dedicated view for fetching group members"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, group_id):
        """Get group members"""
        try:
            group = GroupChat.objects.get(id=group_id)
            if request.user not in group.members.all():
                return Response({'error': 'Not a member of this group'}, status=status.HTTP_403_FORBIDDEN)
            
            serializer = GroupChatSerializer(group, context={'request': request})
            return Response(serializer.data)
        except GroupChat.DoesNotExist:
            return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)


class GroupChatListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        current_user = request.user
        
        # 🚀 SPEED: Try to get cached group conversations first
        cache_key = f"user_group_conversations_{current_user.id}"
        cached_groups = cache.get(cache_key)
        
        if cached_groups:
            logger.info(f"🚀 Cache HIT: Returning cached group conversations for user {current_user.id}")
            return Response(cached_groups)
        
        # 🚀 SPEED: Optimized query with prefetch_related
        groups = GroupChat.objects.filter(members=current_user).prefetch_related(
            'members', 'admins'
        ).select_related()
        
        # Transform groups to include unread count and last message info
        group_conversations = []
        for group in groups:
            # 🚀 SPEED: Get the latest message in this group
            latest_message = Message.objects.filter(group=group).select_related('sender').order_by('-timestamp').first()
            
            # 🚀 SPEED: Calculate unread count for this user in this group
            # Similar to private messages: count messages from others that this user hasn't "read"
            # A message is considered "read" if there's a MessageRead record for this user
            unread_messages = Message.objects.filter(
                group=group
            ).exclude(sender=current_user)
            
            read_message_ids = MessageRead.objects.filter(
                user=current_user,
                message__group=group
            ).values_list('message_id', flat=True)
            
            unread_count = unread_messages.exclude(id__in=read_message_ids).count()
            
            # Build group conversation object
            group_data = {
                'id': group.id,
                'type': 'group',
                'group': {
                    'id': group.id,
                    'name': group.name,
                    'description': group.description,
                    'group_picture': request.build_absolute_uri(group.group_picture.url) if group.group_picture else None,
                    'members': [
                        {
                            'id': member.id,
                            'username': member.username,
                            'first_name': member.first_name,
                            'last_name': member.last_name,
                            'profile_picture': request.build_absolute_uri(member.profile_picture.url) if member.profile_picture else None
                        } for member in group.members.all()
                    ],
                    'admins': [admin.id for admin in group.admins.all()],
                    'created_at': group.created_at.isoformat(),
                    'updated_at': group.updated_at.isoformat()
                },
                'lastMessage': latest_message.content[:50] + ('...' if latest_message and len(latest_message.content) > 50 else '') if latest_message else 'No messages yet',
                'timestamp': latest_message.timestamp.isoformat() if latest_message else group.created_at.isoformat(),
                'unreadCount': unread_count
            }
            group_conversations.append(group_data)
        
        # Sort by timestamp (newest first)
        group_conversations.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # 🚀 SPEED: Cache for 10 seconds (group conversations change frequently)
        cache.set(cache_key, group_conversations, 10)
        logger.info(f"🚀 Cache MISS: Cached group conversations for user {current_user.id}")
        
        return Response(group_conversations)
