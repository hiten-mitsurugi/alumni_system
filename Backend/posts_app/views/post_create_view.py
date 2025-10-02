from django.core.cache import cache
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from ..models import Post
from ..serializers import PostCreateSerializer, PostSerializer


class PostCreateView(APIView):
    """Create new posts with auto-approval for admins"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Create a new post with real-time broadcasting"""
        serializer = PostCreateSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            post = serializer.save()
            
            # Invalidate feed cache
            self._invalidate_feed_cache()
            
            # Broadcast new post to relevant users
            self._broadcast_new_post(post, request.user)
            
            # Return full post data
            response_serializer = PostSerializer(post, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _invalidate_feed_cache(self):
        """Invalidate all feed caches"""
        try:
            # This is a simplified approach - in production, you'd want more targeted cache invalidation
            cache.delete_many(cache.keys('post_feed_*'))
        except:
            pass
    
    def _broadcast_new_post(self, post, user):
        """Broadcast new post to real-time subscribers"""
        channel_layer = get_channel_layer()
        
        # Since all posts are now auto-approved, always broadcast to all users
        async_to_sync(channel_layer.group_send)(
            'posts_feed',
            {
                'type': 'new_post',
                'post_id': post.id,
                'user_id': user.id,
                'timestamp': post.created_at.isoformat()
            }
        )