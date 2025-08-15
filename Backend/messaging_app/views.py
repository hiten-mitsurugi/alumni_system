
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from .models import Message, GroupChat, MessageRequest, BlockedUser
from .serializers import UserSerializer, GroupChatSerializer, MessageSerializer, MessageRequestSerializer, BlockedUserSerializer, AttachmentSerializer, ReactionSerializer, UserSearchSerializer
from .link_utils import create_link_previews_for_message
import logging
from django.conf import settings
from django.core.files.storage import FileSystemStorage

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

        # Get all users blocked by current user (for marking blocked status)
        blocked_user_ids = BlockedUser.objects.filter(user=current_user).values_list('blocked_user_id', flat=True)
        
        # Get all users who blocked current user (for marking blocked status)
        blocked_by_user_ids = BlockedUser.objects.filter(blocked_user=current_user).values_list('user_id', flat=True)

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

        # Get conversation details for each user
        conversations = []
        for user_id, conv_data in conversation_dict.items():
            try:
                other_user = User.objects.get(id=user_id)
                
                # Get the latest message between these users
                latest_message = Message.objects.filter(
                    Q(sender=current_user, receiver=other_user) |
                    Q(sender=other_user, receiver=current_user)
                ).order_by('-timestamp').first()

                if latest_message:
                    # Build absolute URL for profile picture
                    profile_picture_url = None
                    if other_user.profile_picture:
                        profile_picture_url = request.build_absolute_uri(other_user.profile_picture.url)
                    
                    # Check blocking status
                    is_blocked_by_me = other_user.id in blocked_user_ids
                    is_blocked_by_them = other_user.id in blocked_by_user_ids
                    
                    # Create conversation object
                    conversation = {
                        'type': 'private',
                        'mate': {
                            'id': other_user.id,
                            'username': other_user.username,
                            'first_name': other_user.first_name,
                            'last_name': other_user.last_name,
                            'profile_picture': profile_picture_url,
                            'profile': {
                                'status': getattr(other_user.profile, 'status', 'offline') if hasattr(other_user, 'profile') else 'offline',
                                'last_seen': getattr(other_user.profile, 'last_seen', None) if hasattr(other_user, 'profile') else None,
                            }
                        },
                        'lastMessage': latest_message.content[:50] + ('...' if len(latest_message.content) > 50 else ''),
                        'timestamp': latest_message.timestamp.isoformat(),
                        'unreadCount': Message.objects.filter(
                            sender=other_user,
                            receiver=current_user,
                            is_read=False
                        ).count(),
                        'isBlockedByMe': is_blocked_by_me,
                        'isBlockedByThem': is_blocked_by_them,
                        'canSendMessage': not (is_blocked_by_me or is_blocked_by_them)
                    }
                    conversations.append(conversation)
            except User.DoesNotExist:
                continue

        # Sort by timestamp (newest first)
        conversations.sort(key=lambda x: x['timestamp'], reverse=True)

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
            
            serializer = MessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

class MessageListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, receiver_id=None, group_id=None):
        if group_id:
            # Handle group messages
            try:
                group = GroupChat.objects.get(id=group_id)
                # Check if user is a member of the group
                if request.user not in group.members.all():
                    return Response({"error": "You are not a member of this group"}, status=status.HTTP_403_FORBIDDEN)
                
                # Fetch group messages
                messages = Message.objects.filter(group=group).order_by("timestamp")
                serializer = MessageSerializer(messages, many=True, context={'request': request})
                return Response(serializer.data)
                
            except GroupChat.DoesNotExist:
                return Response({"error": "Group not found"}, status=status.HTTP_404_NOT_FOUND)
        
        elif receiver_id:
            # Handle private messages
            try:
                receiver = User.objects.get(id=receiver_id)
            except (User.DoesNotExist, ValueError):
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            # Don't block message viewing - let users see their conversation history
            # Only block sending new messages (handled in SendMessageView)
            
            # Fetch messages
            messages = Message.objects.filter(
                sender=request.user, receiver=receiver
            ) | Message.objects.filter(
                sender=receiver, receiver=request.user
            )
            messages = messages.order_by("timestamp")

            serializer = MessageSerializer(messages, many=True, context={'request': request})
            return Response(serializer.data)
        
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
    def post(self, request, group_id):
        group = GroupChat.objects.get(id=group_id)
        if request.user not in group.admins.all():
            return Response({'error': 'Not an admin'}, status=status.HTTP_403_FORBIDDEN)
        action = request.data.get('action')
        user_id = request.data.get('user_id')
        if action == 'add_member':
            group.members.add(user_id)
        elif action == 'remove_member':
            group.members.remove(user_id)
        elif action == 'promote_admin':
            group.admins.add(user_id)
        elif action == 'demote_admin':
            group.admins.remove(user_id)
        serializer = GroupChatSerializer(group)
        return Response(serializer.data)

class GroupChatListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        groups = GroupChat.objects.filter(members=request.user)
        serializer = GroupChatSerializer(groups, many=True)
        return Response(serializer.data)

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