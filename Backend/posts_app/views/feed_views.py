"""
Feed-related views for posts_app.

This module handles post feed display, post creation, and post detail retrieval.
"""

from django.db.models import Q, Prefetch
from django.core.cache import cache
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from ..models import Post, Comment, PostView
from ..serializers import PostSerializer, PostCreateSerializer
from .base_views import PostPagination


class PostFeedView(APIView):
    """Facebook-style post feed with real-time updates and caching"""
    permission_classes = [IsAuthenticated]
    pagination_class = PostPagination
    
    def get(self, request):
        """Get paginated post feed with filtering and caching"""
        user = request.user
        category = request.query_params.get('category')
        search = request.query_params.get('search')
        page = int(request.query_params.get('page', 1))
        
        # Create cache key
        cache_key = f"post_feed_{user.id}_{category}_{search}_{page}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            # Track post views for analytics
            self._track_post_views(cached_data.get('results', []), user, request)
            return Response(cached_data)
        
        # Build query based on user type and filters
        queryset = self._build_feed_queryset(user, category, search)
        
        # Paginate results
        paginator = self.pagination_class()
        paginated_posts = paginator.paginate_queryset(queryset, request)
        
        # Serialize with full context
        serializer = PostSerializer(
            paginated_posts, 
            many=True, 
            context={'request': request}
        )
        
        # Get paginated response
        response_data = paginator.get_paginated_response(serializer.data).data
        
        # Cache for 5 minutes
        cache.set(cache_key, response_data, 300)
        
        # Track post views
        self._track_post_views(response_data.get('results', []), user, request)
        
        return Response(response_data)
    
    def _build_feed_queryset(self, user, category, search):
        """Build optimized queryset for post feed"""
        queryset = Post.objects.select_related(
            'user', 'category', 'shared_post__user'
        ).prefetch_related(
            'media_files',
            Prefetch('comments', queryset=Comment.objects.select_related('user').order_by('-created_at'))
        )
        
        # Apply visibility filters based on user type
        # Admins (type 1 & 2) see ALL posts regardless of status or visibility
        # Alumni (type 3) only see published posts and exclude admin-only visibility
        if user.user_type == 3:  # Alumni
            queryset = queryset.filter(status='published').exclude(visibility='admin_only')
        # For admins, no filtering - they see everything
        
        # Apply category filter
        if category and category != 'all':
            queryset = queryset.filter(content_category=category)
        
        # Apply search filter
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(content__icontains=search) |
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search)
            )
        
        return queryset.order_by('-is_pinned', '-created_at')
    
    def _track_post_views(self, posts, user, request):
        """Track post views for analytics"""
        try:
            for post_data in posts:
                PostView.objects.get_or_create(
                    post_id=post_data['id'],
                    user=user,
                    defaults={
                        'ip_address': self._get_client_ip(request),
                        'user_agent': request.META.get('HTTP_USER_AGENT', '')
                    }
                )
        except Exception as e:
            # Don't fail the request if view tracking fails
            pass
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')


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
