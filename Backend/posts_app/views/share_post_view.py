from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from ..models import Post
from ..serializers import PostSerializer


class SharePostView(APIView):
    """Share/repost functionality"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, post_id):
        """Share a post with optional text"""
        try:
            original_post = Post.objects.get(id=post_id)
            shared_text = request.data.get('shared_text', '').strip()
            
            # Create shared post
            shared_post = Post.objects.create(
                user=request.user,
                content=shared_text or f"Shared a post by {original_post.user.first_name}",
                content_category=original_post.content_category,
                post_type='shared',
                shared_post=original_post,
                shared_text=shared_text,
                is_approved=True  # All posts are now auto-approved
            )
            
            # Update share count
            original_post.shares_count += 1
            original_post.save(update_fields=['shares_count'])
            
            # Broadcast share
            self._broadcast_post_share(shared_post, original_post, request.user)
            
            serializer = PostSerializer(shared_post, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Post.DoesNotExist:
            return Response(
                {'error': 'Post not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    def _broadcast_post_share(self, shared_post, original_post, user):
        """Broadcast post share to real-time subscribers"""
        channel_layer = get_channel_layer()
        
        # Notify original post author
        async_to_sync(channel_layer.group_send)(
            f'user_{original_post.user.id}',
            {
                'type': 'post_shared',
                'original_post_id': original_post.id,
                'shared_post_id': shared_post.id,
                'sharer_id': user.id,
                'sharer_name': f"{user.first_name} {user.last_name}",
                'timestamp': shared_post.created_at.isoformat()
            }
        )