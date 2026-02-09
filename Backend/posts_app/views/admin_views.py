"""
Admin-related views for posts_app.

This module handles admin operations like post approval, pinning, and deletion.
"""

from django.core.cache import cache
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from ..models import Post
from ..serializers import PostSerializer
from .base_views import IsAdminOrSuperAdmin


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


class PostPinView(APIView):
    """Pin/unpin posts (admin only)"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, post_id):
        """Pin or unpin a post"""
        # Check if user is admin
        if not hasattr(request.user, 'user_type') or request.user.user_type not in [1, 2]:
            return Response(
                {'error': 'Admin access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            post = Post.objects.get(id=post_id)
            
            # Toggle pin status
            post.is_pinned = not post.is_pinned
            post.save()
            
            # Invalidate cache
            cache.delete_many(cache.keys('post_feed_*'))
            
            return Response({
                'message': f'Post {"pinned" if post.is_pinned else "unpinned"} successfully',
                'is_pinned': post.is_pinned
            }, status=status.HTTP_200_OK)
            
        except Post.DoesNotExist:
            return Response(
                {'error': 'Post not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class PostDeleteView(APIView):
    """Delete posts (admin or owner only)"""
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, post_id):
        """Delete a post"""
        try:
            post = Post.objects.get(id=post_id)
            
            # Check permissions: admin or post owner
            is_admin = hasattr(request.user, 'user_type') and request.user.user_type in [1, 2]
            is_owner = post.user == request.user
            
            if not (is_admin or is_owner):
                return Response(
                    {'error': 'Permission denied. Only admins or post owners can delete posts.'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Store post data for broadcasting before deletion
            post_data = {
                'id': post.id,
                'user_id': post.user.id,
                'title': post.title,
                'content': post.content[:50] + '...' if len(post.content) > 50 else post.content
            }
            
            # Delete the post
            post.delete()
            
            # Comprehensive cache invalidation
            self._invalidate_all_post_caches(post_id)
            
            # Broadcast post deletion to WebSocket subscribers
            self._broadcast_post_deletion(post_data, request.user)
            
            return Response({
                'message': 'Post deleted successfully'
            }, status=status.HTTP_200_OK)
            
        except Post.DoesNotExist:
            return Response(
                {'error': 'Post not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    def _invalidate_all_post_caches(self, post_id):
        """Comprehensive cache invalidation for post deletion"""
        try:
            # Clear specific post cache
            cache.delete(f"post_{post_id}")
            cache.delete(f"post_reactions_{post_id}")
            cache.delete(f"post_comments_{post_id}")
            
            # Clear all feed caches
            cache.clear()
            
            # Set a cache invalidation flag
            cache.set('posts_cache_invalidated', True, 60)
            
        except Exception as e:
            print(f"Cache invalidation error: {e}")
    
    def _broadcast_post_deletion(self, post_data, deleting_user):
        """Broadcast post deletion to WebSocket subscribers"""
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        
        # Broadcast to general posts feed
        async_to_sync(channel_layer.group_send)(
            'posts_feed',
            {
                'type': 'post_deleted',
                'post_id': post_data['id'],
                'deleted_by_user_id': deleting_user.id,
                'deleted_by_name': f"{deleting_user.first_name} {deleting_user.last_name}",
                'message': 'Post deleted successfully',
                'timestamp': timezone.now().isoformat()
            }
        )
        
        # Broadcast to specific post group (for anyone viewing the post)
        async_to_sync(channel_layer.group_send)(
            f'post_{post_data["id"]}',
            {
                'type': 'post_deleted',
                'post_id': post_data['id'],
                'deleted_by_user_id': deleting_user.id,
                'deleted_by_name': f"{deleting_user.first_name} {deleting_user.last_name}",
                'message': 'Post deleted successfully',
                'timestamp': timezone.now().isoformat()
            }
        )
