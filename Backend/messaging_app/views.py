
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from .models import Message, GroupChat, MessageRequest, BlockedUser, GroupMemberRequest, MessageRead
from .serializers import UserSerializer, GroupChatSerializer, MessageSerializer, MessageRequestSerializer, BlockedUserSerializer, AttachmentSerializer, ReactionSerializer, UserSearchSerializer, GroupMemberRequestSerializer
from .link_utils import create_link_previews_for_message
import logging
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import uuid

# Initialize logger
logger = logging.getLogger(__name__)
from .models import Attachment
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

class SearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response({"users": [], "groups": []}, status=status.HTTP_200_OK)

        # Get blocked users to mark them as blocked (but still show them in search)
        blocked_user_ids = BlockedUser.objects.filter(user=request.user).values_list('blocked_user_id', flat=True)
        blocked_by_user_ids = BlockedUser.objects.filter(blocked_user=request.user).values_list('user_id', flat=True)

        # ✅ Search users (show all users, don't exclude blocked ones)
        users_qs = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).exclude(
            id=request.user.id  # Only exclude self
        )

        # ✅ Apply optional filters if they exist
        if hasattr(User, 'is_approved'):
            users_qs = users_qs.filter(is_approved=True)
        if hasattr(User, 'user_type'):
            users_qs = users_qs.filter(user_type=3)

        users = users_qs.distinct()

        # ✅ Search groups
        groups = GroupChat.objects.filter(name__icontains=query)

        # ✅ Serialize using EXISTING serializers
        user_serializer = UserSearchSerializer(users, many=True, context={"request": request})
        group_serializer = GroupChatSerializer(groups, many=True)

        return Response({
            "users": user_serializer.data,
            "groups": group_serializer.data
        }, status=status.HTTP_200_OK)

        
        
class ConversationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.db.models import F, Max, Q
        
        current_user = request.user
        
        # 🚀 SPEED: Try to get cached conversations first
        cache_key = f"user_conversations_{current_user.id}"
        cached_conversations = cache.get(cache_key)
        
        if cached_conversations:
            logger.info(f"🚀 Cache HIT: Returning cached conversations for user {current_user.id}")
            return Response(cached_conversations, status=status.HTTP_200_OK)

        # Get all users blocked by current user (for marking blocked status)
        blocked_user_ids = set(BlockedUser.objects.filter(user=current_user).values_list('blocked_user_id', flat=True))
        
        # Get all users who blocked current user (for marking blocked status)
        blocked_by_user_ids = set(BlockedUser.objects.filter(blocked_user=current_user).values_list('user_id', flat=True))

        # 🚀 SPEED: Optimized query with select_related and prefetch_related
        # Get conversations from both sent and received messages (DO NOT filter out blocked users)
        sent_conversations = Message.objects.filter(
            sender=current_user,
            receiver__isnull=False
        ).values('receiver').annotate(
            other_user_id=F('receiver'),
            last_message_time=Max('timestamp')
        )

        received_conversations = Message.objects.filter(
            receiver=current_user,
            sender__isnull=False
        ).values('sender').annotate(
            other_user_id=F('sender'),
            last_message_time=Max('timestamp')
        )

        # Combine and get unique conversations
        all_conversations = list(sent_conversations) + list(received_conversations)
        
        # Group by other_user_id and get the latest timestamp
        conversation_dict = {}
        for conv in all_conversations:
            user_id = conv['other_user_id']
            if user_id not in conversation_dict or conv['last_message_time'] > conversation_dict[user_id]['last_message_time']:
                conversation_dict[user_id] = conv

        # 🚀 SPEED: Batch fetch all users at once to reduce DB queries
        user_ids = list(conversation_dict.keys())
        users_data = User.objects.filter(id__in=user_ids).select_related('profile').values(
            'id', 'username', 'first_name', 'last_name', 'profile_picture',
            'profile__status', 'profile__last_seen'
        )
        users_dict = {user['id']: user for user in users_data}

        # 🚀 SPEED: Batch fetch latest messages for all conversations
        latest_messages_qs = Message.objects.filter(
            Q(sender=current_user, receiver_id__in=user_ids) |
            Q(sender_id__in=user_ids, receiver=current_user)
        ).select_related('sender', 'receiver').order_by('receiver_id', 'sender_id', '-timestamp')
        
        # Group latest messages by conversation
        latest_messages_dict = {}
        for msg in latest_messages_qs:
            # Determine the other user
            other_user_id = msg.receiver_id if msg.sender_id == current_user.id else msg.sender_id
            
            # Only keep the latest message for each conversation
            if other_user_id not in latest_messages_dict:
                latest_messages_dict[other_user_id] = msg

        # 🚀 SPEED: Batch count unread messages for all conversations
        unread_counts = Message.objects.filter(
            sender_id__in=user_ids,
            receiver=current_user,
            is_read=False
        ).values('sender_id').annotate(unread_count=F('id')).values_list('sender_id', 'unread_count')
        unread_dict = {sender_id: count for sender_id, count in unread_counts}

        # Get conversation details for each user
        conversations = []
        for user_id, conv_data in conversation_dict.items():
            if user_id not in users_dict:
                continue
                
            other_user_data = users_dict[user_id]
            latest_message = latest_messages_dict.get(user_id)

            if latest_message:
                # Build absolute URL for profile picture
                profile_picture_url = None
                if other_user_data['profile_picture']:
                    profile_picture_url = request.build_absolute_uri(other_user_data['profile_picture'])
                
                # Check blocking status
                is_blocked_by_me = user_id in blocked_user_ids
                is_blocked_by_them = user_id in blocked_by_user_ids
                
                # Create conversation object
                conversation = {
                    'type': 'private',
                    'mate': {
                        'id': user_id,
                        'username': other_user_data['username'],
                        'first_name': other_user_data['first_name'],
                        'last_name': other_user_data['last_name'],
                        'profile_picture': profile_picture_url,
                        'profile': {
                            'status': other_user_data.get('profile__status', 'offline'),
                            'last_seen': other_user_data.get('profile__last_seen'),
                        }
                    },
                    'lastMessage': latest_message.content[:50] + ('...' if len(latest_message.content) > 50 else ''),
                    'timestamp': latest_message.timestamp.isoformat(),
                    'unreadCount': unread_dict.get(user_id, 0),
                    'isBlockedByMe': is_blocked_by_me,
                    'isBlockedByThem': is_blocked_by_them,
                    'canSendMessage': not (is_blocked_by_me or is_blocked_by_them)
                }
                conversations.append(conversation)

        # Sort by timestamp (newest first)
        conversations.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # 🚀 SPEED: Cache for 10 seconds (conversations change frequently)
        cache.set(cache_key, conversations, 10)
        logger.info(f"🚀 Cache MISS: Cached conversations for user {current_user.id}")

        return Response(conversations, status=status.HTTP_200_OK)

class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        receiver_id = request.data.get('receiver_id')
        content = request.data.get('content')
        reply_to_id = request.data.get('reply_to_id')
        attachment_ids = request.data.get('attachment_ids', [])

        if not receiver_id or not content:
            return Response({'error': 'Receiver ID and content required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            receiver = User.objects.get(id=receiver_id)
        except User.DoesNotExist:
            return Response({'error': 'Receiver not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if current user is blocked by receiver
        is_blocked_by_receiver = BlockedUser.objects.filter(
            user=receiver, 
            blocked_user=request.user
        ).exists()
        
        if is_blocked_by_receiver:
            return Response({
                'error': 'You cannot send messages to this user. You have been blocked.'
            }, status=status.HTTP_403_FORBIDDEN)

        # Check if current user has blocked the receiver
        has_blocked_receiver = BlockedUser.objects.filter(
            user=request.user, 
            blocked_user=receiver
        ).exists()
        
        if has_blocked_receiver:
            return Response({
                'error': 'You cannot send messages to a user you have blocked. Please unblock them first.'
            }, status=status.HTTP_403_FORBIDDEN)

        # Check if there's an existing conversation (either messages exist OR accepted message requests exist)
        has_conversation = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=receiver)) |
            (Q(sender=receiver) & Q(receiver=request.user))
        ).exists() or MessageRequest.objects.filter(
            (Q(sender=request.user) & Q(receiver=receiver)) |
            (Q(sender=receiver) & Q(receiver=request.user)),
            accepted=True
        ).exists()

        if not has_conversation:
            # Create a message request if no prior conversation
            message_request = MessageRequest.objects.create(
                sender=request.user,
                receiver=receiver,
                content=content,
                timestamp=timezone.now()
            )
            return Response({
                'status': 'Message request sent',
                'request_id': str(message_request.id)
            }, status=status.HTTP_201_CREATED)
        else:
            # Create message if conversation exists
            message = Message.objects.create(
                sender=request.user,
                receiver=receiver,
                content=content
            )
            
            # Add reply_to if provided
            if reply_to_id:
                try:
                    reply_message = Message.objects.get(id=reply_to_id)
                    message.reply_to = reply_message
                    message.save()
                except Message.DoesNotExist:
                    pass
            
            # Add attachments
            for attachment_id in attachment_ids:
                try:
                    attachment = Attachment.objects.get(id=attachment_id)
                    message.attachments.add(attachment)
                except Attachment.DoesNotExist:
                    pass
            
            # Generate link previews automatically
            try:
                create_link_previews_for_message(message)
            except Exception as e:
                logger.error(f"Failed to create link previews for message {message.id}: {str(e)}")
            
            # 🚀 SPEED: Invalidate caches after sending message
            # Clear conversation caches for both sender and receiver
            cache.delete(f"user_conversations_{request.user.id}")
            cache.delete(f"user_conversations_{receiver.id}")
            
            # Clear message cache for this conversation
            user_ids = sorted([request.user.id, receiver.id])
            cache.delete(f"private_messages_{user_ids[0]}_{user_ids[1]}")
            
            logger.info(f"🚀 Cache invalidated after message sent from {request.user.id} to {receiver.id}")
            
            serializer = MessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

class MessageListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, receiver_id=None, group_id=None):
        if group_id:
            # Handle group messages with Redis caching
            try:
                group = GroupChat.objects.get(id=group_id)
                # Check if user is a member of the group
                if request.user not in group.members.all():
                    return Response({"error": "You are not a member of this group"}, status=status.HTTP_403_FORBIDDEN)
                
                # 🚀 SPEED: Try to get cached group messages first
                cache_key = f"group_messages_{group_id}_{request.user.id}"
                cached_messages = cache.get(cache_key)
                
                if cached_messages:
                    logger.info(f"🚀 Cache HIT: Returning cached group messages for group {group_id}")
                    return Response(cached_messages)
                
                # Fetch group messages with optimized query
                messages = Message.objects.filter(group=group).select_related(
                    'sender', 'sender__profile', 'reply_to', 'reply_to__sender'
                ).prefetch_related(
                    'attachments', 'reactions', 'reactions__user'
                ).order_by("timestamp")
                
                serializer = MessageSerializer(messages, many=True, context={'request': request})
                serialized_data = serializer.data
                
                # 🚀 SPEED: Cache for 30 seconds (messages change frequently)
                cache.set(cache_key, serialized_data, 30)
                logger.info(f"🚀 Cache MISS: Cached group messages for group {group_id}")
                
                return Response(serialized_data)
                
            except GroupChat.DoesNotExist:
                return Response({"error": "Group not found"}, status=status.HTTP_404_NOT_FOUND)
        
        elif receiver_id:
            # Handle private messages with Redis caching
            try:
                receiver = User.objects.get(id=receiver_id)
            except (User.DoesNotExist, ValueError):
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            # 🚀 SPEED: Try to get cached private messages first
            # Use sorted IDs to ensure same cache key regardless of sender/receiver order
            user_ids = sorted([request.user.id, receiver_id])
            cache_key = f"private_messages_{user_ids[0]}_{user_ids[1]}"
            cached_messages = cache.get(cache_key)
            
            if cached_messages:
                logger.info(f"🚀 Cache HIT: Returning cached private messages for users {user_ids}")
                return Response(cached_messages)

            # Don't block message viewing - let users see their conversation history
            # Only block sending new messages (handled in SendMessageView)
            
            # Fetch messages with optimized query
            messages = Message.objects.filter(
                sender=request.user, receiver=receiver
            ) | Message.objects.filter(
                sender=receiver, receiver=request.user
            )
            messages = messages.select_related(
                'sender', 'sender__profile', 'receiver', 'receiver__profile', 
                'reply_to', 'reply_to__sender'
            ).prefetch_related(
                'attachments', 'reactions', 'reactions__user'
            ).order_by("timestamp")

            serializer = MessageSerializer(messages, many=True, context={'request': request})
            serialized_data = serializer.data
            
            # 🚀 SPEED: Cache for 30 seconds (messages change frequently)
            cache.set(cache_key, serialized_data, 30)
            logger.info(f"🚀 Cache MISS: Cached private messages for users {user_ids}")
            
            return Response(serialized_data)
        
        else:
            return Response({"error": "Either receiver_id or group_id must be provided"}, status=status.HTTP_400_BAD_REQUEST)

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
                        from .models import Message
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
                        from .models import Message
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
                        from .models import Message
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

class ConversationUsersView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        users = settings.AUTH_USER_MODEL.objects.filter(
            Q(sent_messages__receiver=user) | Q(received_messages__sender=user)
        ).distinct()
        serializer = UserSearchSerializer(users, many=True, context={'request': request})
        return Response(serializer.data)

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
            msg_request.delete()
            return Response({'status': 'Request declined'})
        return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

class BlockUserView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get list of users blocked by current user"""
        blocked_users = BlockedUser.objects.filter(user=request.user)
        serializer = BlockedUserSerializer(blocked_users, many=True, context={'request': request})
        return Response(serializer.data)
    
    def post(self, request):
        """Block a user"""
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user_to_block = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Prevent self-blocking
        if user_to_block == request.user:
            return Response({'error': 'You cannot block yourself'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if already blocked
        existing_block = BlockedUser.objects.filter(
            user=request.user, 
            blocked_user=user_to_block
        ).first()
        
        if existing_block:
            return Response({'error': 'User is already blocked'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create block relationship
        blocked_user = BlockedUser.objects.create(
            user=request.user, 
            blocked_user=user_to_block
        )
        
        # Send real-time notification via WebSocket
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'user_{user_to_block.id}',
                {
                    'type': 'user_blocked',
                    'message': f'You have been blocked by {request.user.first_name} {request.user.last_name}',
                    'blocked_by': request.user.id
                }
            )
        except Exception as e:
            logger.error(f"Failed to send block notification: {str(e)}")
        
        serializer = BlockedUserSerializer(blocked_user, context={'request': request})
        return Response({
            'status': 'User blocked successfully',
            'blocked_user': serializer.data
        }, status=status.HTTP_201_CREATED)
        
    def delete(self, request, user_id):
        """Unblock a user"""
        try:
            user_to_unblock = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Find and delete the block relationship
        blocked_user = BlockedUser.objects.filter(
            user=request.user, 
            blocked_user=user_to_unblock
        ).first()
        
        if not blocked_user:
            return Response({'error': 'User is not blocked'}, status=status.HTTP_400_BAD_REQUEST)
        
        blocked_user.delete()
        
        # Send real-time notification via WebSocket
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'user_{user_to_unblock.id}',
                {
                    'type': 'user_unblocked',
                    'message': f'You have been unblocked by {request.user.first_name} {request.user.last_name}',
                    'unblocked_by': request.user.id
                }
            )
        except Exception as e:
            logger.error(f"Failed to send unblock notification: {str(e)}")
        
        return Response({
            'status': 'User unblocked successfully'
        }, status=status.HTTP_200_OK)



class SearchUsersView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        query = request.GET.get('q', '')
        
        # Get blocked users to exclude from search
        blocked_user_ids = BlockedUser.objects.filter(user=request.user).values_list('blocked_user_id', flat=True)
        blocked_by_user_ids = BlockedUser.objects.filter(blocked_user=request.user).values_list('user_id', flat=True)
        
        # Combine both lists to exclude all blocked relationships
        excluded_user_ids = list(blocked_user_ids) + list(blocked_by_user_ids)
        
        users = User.objects.filter(
            Q(username__icontains=query) | 
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query)
        ).exclude(
            id=request.user.id  # Exclude self
        ).exclude(
            id__in=excluded_user_ids  # Exclude blocked users
        )
        
        serializer = UserSearchSerializer(users, many=True, context={'request': request})
        return Response(serializer.data)

class PinMessageView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, message_id):
        """Pin or unpin a message"""
        try:
            message = get_object_or_404(Message, id=message_id)
            
            # Check if user has permission to pin this message
            # For private messages: either sender or receiver can pin
            # For group messages: any group member can pin
            can_pin = False
            
            if message.receiver:  # Private message
                if request.user == message.sender or request.user == message.receiver:
                    can_pin = True
            elif message.group:  # Group message
                if request.user in message.group.members.all():
                    can_pin = True
            
            if not can_pin:
                return Response({
                    'error': 'You do not have permission to pin this message'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Toggle pin status
            message.is_pinned = not message.is_pinned
            message.save()
            
            # Send real-time notification via WebSocket
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            
            channel_layer = get_channel_layer()
            
            # Prepare message data for WebSocket
            serializer = MessageSerializer(message, context={'request': request})
            
            if message.receiver:  # Private message
                # Notify both sender and receiver
                for user_id in [message.sender.id, message.receiver.id]:
                    async_to_sync(channel_layer.group_send)(
                        f'user_{user_id}',
                        {
                            'type': 'message_pinned',
                            'message': serializer.data,
                            'action': 'pin' if message.is_pinned else 'unpin'
                        }
                    )
            elif message.group:  # Group message
                # Notify all group members
                async_to_sync(channel_layer.group_send)(
                    f'group_{message.group.id}',
                    {
                        'type': 'message_pinned',
                        'message': serializer.data,
                        'action': 'pin' if message.is_pinned else 'unpin'
                    }
                )
            
            return Response({
                'status': f'Message {"pinned" if message.is_pinned else "unpinned"} successfully',
                'message': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error pinning/unpinning message {message_id}: {e}")
            return Response({
                'error': 'Failed to pin/unpin message'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class BumpMessageView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, message_id):
        """
        Bump a message - creates a new message that references the original.
        Like Facebook Messenger's bump feature.
        """
        try:
            # Get the original message - must be sender's own message
            original_message = get_object_or_404(
                Message, 
                id=message_id, 
                sender=request.user
            )
            
            # Determine the receiver based on original message type
            if original_message.receiver:
                # Private message - bump to same receiver
                receiver = original_message.receiver
                group = None
            elif original_message.group:
                # Group message - bump to same group
                receiver = None
                group = original_message.group
                
                # Check if user is still a member of the group
                if request.user not in group.members.all():
                    return Response({
                        'error': 'You are no longer a member of this group'
                    }, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({
                    'error': 'Invalid message type'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create the bump message
            bump_message = Message.objects.create(
                sender=request.user,
                receiver=receiver,
                group=group,
                content=f"🔔 Bumped message",  # Special content indicating this is a bump
                reply_to=original_message  # Reference to original message
            )
            
            # Serialize the new bump message with full relationships
            bump_message_with_relations = Message.objects.select_related(
                'sender', 'receiver', 'group', 'reply_to', 'reply_to__sender'
            ).prefetch_related('attachments').get(id=bump_message.id)
            
            serializer = MessageSerializer(
                bump_message_with_relations, 
                context={'request': request}
            )
            
            # Send real-time notification via WebSocket
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            
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

class UploadView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        file = request.FILES['file']
        # Create attachment directly like profile picture upload
        attachment = Attachment.objects.create(
            file=file,
            file_type=file.content_type
        )
        return Response({'id': str(attachment.id)}, status=status.HTTP_201_CREATED)

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

class MessageSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Search messages within a specific conversation.
        Query params:
          - scope: 'private' or 'group'
          - id: other user id (for private) or group uuid (for group)
          - q: search query (required, min 1 char)
          - limit: optional max messages to scan (default 1000)
        Returns list of { id, content_snippet, timestamp, sender, match_index }
        """
        try:
            query = request.query_params.get('q', '').strip()
            scope = request.query_params.get('scope', '').strip()
            convo_id = request.query_params.get('id', '').strip()
            try:
                scan_limit = int(request.query_params.get('limit', 1000))
            except ValueError:
                scan_limit = 1000

            if not query:
                return Response([], status=status.HTTP_200_OK)

            # Because Message.content is encrypted at rest, database-level icontains filters
            # will not work. We must fetch messages for the conversation and filter in Python.
            base_qs = None

            if scope == 'private':
                try:
                    other_user = User.objects.get(id=convo_id)
                except (User.DoesNotExist, ValueError):
                    return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

                base_qs = Message.objects.filter(
                    (Q(sender=request.user, receiver=other_user) |
                     Q(sender=other_user, receiver=request.user))
                ).order_by('-timestamp')

            elif scope == 'group':
                try:
                    group = GroupChat.objects.get(id=convo_id)
                except (GroupChat.DoesNotExist, ValueError):
                    return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)

                if request.user not in group.members.all():
                    return Response({'error': 'Not a member of this group'}, status=status.HTTP_403_FORBIDDEN)

                base_qs = Message.objects.filter(group=group).order_by('-timestamp')
            else:
                return Response({'error': 'Invalid scope'}, status=status.HTTP_400_BAD_REQUEST)

            # Limit the number of messages we scan for performance
            messages_to_scan = list(base_qs[:scan_limit])

            results = []
            q_lower = query.lower()
            for msg in messages_to_scan:
                content = (msg.content or '')
                idx = content.lower().find(q_lower)
                if idx == -1:
                    continue
                start = max(0, idx - 30)
                end = min(len(content), idx + len(query) + 30)
                snippet = content[start:end]
                if start > 0:
                    snippet = '…' + snippet
                if end < len(content):
                    snippet = snippet + '…'
                results.append({
                    'id': str(msg.id),
                    'timestamp': msg.timestamp.isoformat(),
                    'sender': {
                        'id': msg.sender.id,
                        'first_name': msg.sender.first_name,
                        'last_name': msg.sender.last_name,
                    },
                    'content_snippet': snippet,
                    'match_index': idx
                })

            # Return by chronological order (oldest first) similar to typical UX
            results.reverse()

            return Response(results, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in MessageSearchView: {e}")
            return Response({'error': 'Failed to search messages'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# === MESSAGE REACTIONS VIEWS ===

class MessageReactionView(APIView):
    """Handle adding/removing reactions to messages (Facebook-style)"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Add or update a reaction to a message"""
        try:
            from .models import MessageReaction
            
            message_id = request.data.get('message_id')
            reaction_type = request.data.get('reaction_type')
            
            # Validate required fields
            if not message_id or not reaction_type:
                return Response(
                    {'error': 'message_id and reaction_type are required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate reaction type
            valid_reactions = dict(MessageReaction.REACTION_CHOICES).keys()
            if reaction_type not in valid_reactions:
                return Response(
                    {'error': f'Invalid reaction type. Valid types: {list(valid_reactions)}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
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
            
            # Add or update reaction (one reaction per user per message)
            reaction, created = MessageReaction.objects.update_or_create(
                user=user,
                message=message,
                defaults={'reaction_type': reaction_type}
            )
            
            # Get reaction statistics for this message
            reaction_stats = self.get_reaction_stats(message)
            
            # Broadcast the reaction via WebSocket
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            
            channel_layer = get_channel_layer()
            reaction_data = {
                'type': 'message_reaction',
                'message_id': str(message.id),
                'user_id': user.id,
                'user_name': f"{user.first_name} {user.last_name}".strip() or user.username,
                'reaction_type': reaction_type,
                'emoji': reaction.emoji,
                'action': 'updated' if not created else 'added',
                'reaction_stats': reaction_stats,
                'timestamp': timezone.now().isoformat(),
            }
            
            # Broadcast to private conversation or group
            if message.receiver:
                # Private message - send to both sender and receiver
                for target_user in [message.sender, message.receiver]:
                    async_to_sync(channel_layer.group_send)(
                        f"user_{target_user.id}",
                        reaction_data
                    )
            elif message.group:
                # Group message - send to all group members
                async_to_sync(channel_layer.group_send)(
                    f"group_{message.group.id}",
                    reaction_data
                )
            
            return Response({
                'message': 'Reaction added successfully',
                'reaction': {
                    'id': str(reaction.id),
                    'reaction_type': reaction.reaction_type,
                    'emoji': reaction.emoji,
                    'created': created
                },
                'reaction_stats': reaction_stats
            }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in MessageReactionView POST: {e}")
            return Response(
                {'error': 'Failed to add reaction'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request):
        """Remove a reaction from a message"""
        try:
            from .models import MessageReaction
            
            message_id = request.data.get('message_id')
            
            if not message_id:
                return Response(
                    {'error': 'message_id is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get the message
            try:
                message = Message.objects.get(id=message_id)
            except Message.DoesNotExist:
                return Response(
                    {'error': 'Message not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Remove user's reaction if it exists
            deleted_count = MessageReaction.objects.filter(
                user=request.user,
                message=message
            ).delete()[0]
            
            if deleted_count == 0:
                return Response(
                    {'error': 'No reaction found to remove'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get updated reaction statistics
            reaction_stats = self.get_reaction_stats(message)
            
            # Broadcast the reaction removal via WebSocket
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            
            channel_layer = get_channel_layer()
            reaction_data = {
                'type': 'message_reaction',
                'message_id': str(message.id),
                'user_id': request.user.id,
                'user_name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
                'action': 'removed',
                'reaction_stats': reaction_stats,
                'timestamp': timezone.now().isoformat(),
            }
            
            # Broadcast to private conversation or group
            if message.receiver:
                for target_user in [message.sender, message.receiver]:
                    async_to_sync(channel_layer.group_send)(
                        f"user_{target_user.id}",
                        reaction_data
                    )
            elif message.group:
                async_to_sync(channel_layer.group_send)(
                    f"group_{message.group.id}",
                    reaction_data
                )
            
            return Response({
                'message': 'Reaction removed successfully',
                'reaction_stats': reaction_stats
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in MessageReactionView DELETE: {e}")
            return Response(
                {'error': 'Failed to remove reaction'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get_reaction_stats(self, message):
        """Get reaction statistics for a message"""
        from .models import MessageReaction
        from django.db.models import Count
        
        # Get reaction counts grouped by type
        reaction_counts = MessageReaction.objects.filter(
            message=message
        ).values('reaction_type', 'emoji').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Get users who reacted with each type
        reactions_with_users = {}
        for reaction_type_info in MessageReaction.REACTION_CHOICES:
            reaction_type = reaction_type_info[0]
            reactions = MessageReaction.objects.filter(
                message=message,
                reaction_type=reaction_type
            ).select_related('user')
            
            if reactions.exists():
                reactions_with_users[reaction_type] = {
                    'emoji': reaction_type_info[1],
                    'count': reactions.count(),
                    'users': [
                        {
                            'id': r.user.id,
                            'name': f"{r.user.first_name} {r.user.last_name}".strip() or r.user.username
                        }
                        for r in reactions
                    ]
                }
        
        return {
            'total_reactions': MessageReaction.objects.filter(message=message).count(),
            'reaction_counts': list(reaction_counts),
            'reactions_by_type': reactions_with_users
        }


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
                    from channels.layers import get_channel_layer
                    from asgiref.sync import async_to_sync
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
                        from channels.layers import get_channel_layer
                        from asgiref.sync import async_to_sync
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
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            
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
    """Get unread message and message request counts for the current user"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Return unread counts for messages and message requests"""
        try:
            user = request.user
            
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
            
            return Response({
                'unread_messages': total_unread_messages,
                'unread_private_messages': unread_private_messages,
                'unread_group_messages': unread_group_messages,
                'unread_message_requests': unread_message_requests,
                'total_unread': total_unread_messages + unread_message_requests
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting unread counts for user {request.user.id}: {e}")
            return Response(
                {'error': 'Failed to get unread counts'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )