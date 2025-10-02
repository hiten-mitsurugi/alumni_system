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
                import json
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
