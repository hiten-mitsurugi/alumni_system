from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ..models import Post, PostView
from ..serializers import PostSerializer


class PostDetailView(APIView):
    """Get detailed post information"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, post_id):
        """Get post details with comments and reactions"""
        try:
            post = Post.objects.select_related('user', 'category', 'shared_post').get(id=post_id)
            
            # Check permissions
            if not self._can_view_post(post, request.user):
                return Response(
                    {'error': 'Permission denied'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Track view
            PostView.objects.get_or_create(
                post=post,
                user=request.user,
                defaults={
                    'ip_address': self._get_client_ip(request),
                    'user_agent': request.META.get('HTTP_USER_AGENT', '')
                }
            )
            
            serializer = PostSerializer(post, context={'request': request})
            return Response(serializer.data)
            
        except Post.DoesNotExist:
            return Response(
                {'error': 'Post not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    def _can_view_post(self, post, user):
        """Check if user can view the post"""
        # Admins can see all posts
        if user.user_type in [1, 2]:
            return True
        
        # Since all posts are auto-approved, just check visibility settings
        if post.visibility == 'admin_only' and user.user_type not in [1, 2]:
            return False
        
        return True
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')