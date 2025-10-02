from django.core.cache import cache
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from ..models import Post
from ..serializers import PostSerializer
from .permissions import IsAdminOrSuperAdmin


class PostApprovalView(APIView):
    """Manage post approvals for admins"""
    permission_classes = [IsAdminOrSuperAdmin]
    
    def get(self, request):
        """Get pending posts for approval"""
        posts = Post.objects.filter(is_approved=False).select_related('user').order_by('-created_at')
        serializer = PostSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)
    
    def post(self, request, post_id):
        """Approve a post"""
        try:
            post = Post.objects.get(id=post_id, is_approved=False)
            post.is_approved = True
            post.save()
            
            # Broadcast approval
            self._broadcast_post_approval(post, request.user, approved=True)
            
            # Invalidate cache
            cache.delete_many(cache.keys('post_feed_*'))
            
            return Response({'message': 'Post approved successfully'})
            
        except Post.DoesNotExist:
            return Response(
                {'error': 'Post not found or already approved'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    def delete(self, request, post_id):
        """Reject a post"""
        try:
            post = Post.objects.get(id=post_id, is_approved=False)
            post_user = post.user
            post.delete()
            
            # Broadcast rejection
            self._broadcast_post_approval(post, request.user, approved=False)
            
            return Response({'message': 'Post rejected successfully'})
            
        except Post.DoesNotExist:
            return Response(
                {'error': 'Post not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    def _broadcast_post_approval(self, post, admin_user, approved):
        """Broadcast post approval/rejection to user"""
        channel_layer = get_channel_layer()
        
        async_to_sync(channel_layer.group_send)(
            f'user_{post.user.id}',
            {
                'type': 'post_approval_update',
                'post_id': post.id,
                'approved': approved,
                'admin_name': f"{admin_user.first_name} {admin_user.last_name}",
                'timestamp': timezone.now().isoformat()
            }
        )