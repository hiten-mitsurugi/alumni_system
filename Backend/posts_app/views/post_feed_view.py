from django.db.models import Q, Prefetch
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ..models import Post, Comment, PostView
from ..serializers import PostSerializer
from .pagination import PostPagination


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
        
        # All posts are now auto-approved, so no approval filtering needed
        # Just apply visibility filters based on user type
        if user.user_type == 3:  # Alumni
            queryset = queryset.exclude(visibility='admin_only')
        
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