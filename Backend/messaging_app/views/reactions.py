"""
Message reaction views for adding/removing emoji reactions to messages.
Handles Facebook-style message reactions with real-time WebSocket updates.
"""
import logging
from django.utils import timezone
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from ..models import Message, MessageReaction
from ..serializers import MessageSerializer

logger = logging.getLogger(__name__)


class MessageReactionView(APIView):
    """Handle adding/removing reactions to messages (Facebook-style)"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Add or update a reaction to a message"""
        try:
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
