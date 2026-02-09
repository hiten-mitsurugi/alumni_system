"""
User blocking views for messaging app.
Handles blocking and unblocking users.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth import get_user_model
import logging

from ..models import BlockedUser
from ..serializers import BlockedUserSerializer

logger = logging.getLogger(__name__)
User = get_user_model()


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
