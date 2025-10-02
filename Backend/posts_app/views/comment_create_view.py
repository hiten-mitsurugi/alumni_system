from django.core.cache import cache
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from ..models import Post, Comment
from ..serializers import CommentSerializer, CommentCreateSerializer


class CommentCreateView(APIView):
    """Create and retrieve comments on posts"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, post_id):
        """Get all comments for a post"""
        try:
            post = Post.objects.get(id=post_id)
            
            # Get all comments for this post ordered by creation time
            comments = post.comments.all().order_by('created_at')
            
            serializer = CommentSerializer(comments, many=True, context={'request': request})
            return Response({
                'comments': serializer.data,
                'total_count': post.comments.count()
            }, status=status.HTTP_200_OK)
            
        except Post.DoesNotExist:
            return Response(
                {'error': 'Post not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    def post(self, request, post_id):
        """Create a new comment"""
        try:
            post = Post.objects.get(id=post_id)
            content = request.data.get('content', '').strip()
            parent_id = request.data.get('parent_id')
            
            if not content:
                return Response(
                    {'error': 'Comment content is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create comment
            comment_data = {
                'content': content,
                'parent': parent_id
            }
            
            serializer = CommentCreateSerializer(data=comment_data, context={'request': request})
            if serializer.is_valid():
                comment = serializer.save(user=request.user, post=post)
                
                # Update post comment count immediately and simply
                post.comments_count = post.comments.count()
                post.save(update_fields=['comments_count'])
                
                # Clear all cache to ensure fresh data on refresh - simple approach
                cache.delete(f"post_comments_{post.id}")
                cache.clear()  # Clear all post feed cache variations
                
                # Broadcast new comment AFTER database operations are complete
                self._broadcast_new_comment(comment, request.user)
                
                response_serializer = CommentSerializer(comment, context={'request': request})
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Post.DoesNotExist:
            return Response(
                {'error': 'Post not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    def _update_post_comment_count(self, post):
        """Update post's comment count"""
        count = post.comments.count()
        post.comments_count = count
        post.save(update_fields=['comments_count'])
    
    def _broadcast_new_comment(self, comment, user):
        """Broadcast new comment to real-time subscribers"""
        channel_layer = get_channel_layer()
        
        async_to_sync(channel_layer.group_send)(
            f'post_{comment.post.id}',
            {
                'type': 'new_comment',
                'post_id': comment.post.id,
                'comment_id': comment.id,
                'user_id': user.id,
                'user_name': f"{user.first_name} {user.last_name}",
                'content': comment.content,
                'parent_id': comment.parent.id if comment.parent else None,
                'timestamp': comment.created_at.isoformat()
            }
        )
    
    def _invalidate_post_feed_cache(self):
        """Invalidate post feed cache entries"""
        # Use a simple approach: clear cache by pattern
        # This will force fresh data to be loaded on next request
        cache_patterns = [
            'post_feed_*',  # All post feed cache entries
        ]
        
        # Django's cache doesn't support pattern deletion by default
        # So we'll use a version-based cache invalidation
        cache.delete_many([
            f"post_feed_{i}_{cat}_{search}_{page}" 
            for i in range(1, 50)  # User IDs 1-50
            for cat in ['all', 'announcement', 'job', 'event', 'achievement', 'general', None, '']
            for search in [None, '', 'test']  # Common search terms
            for page in range(1, 6)  # Pages 1-5
        ])