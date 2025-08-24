from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, Count, Prefetch
from django.core.cache import cache
from django.utils import timezone
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Post, Comment, Reaction, PostMedia, SavedPost, PostView, PostReport
from .serializers import (
    PostSerializer, PostCreateSerializer, CommentSerializer, 
    ReactionSerializer, SavedPostSerializer, PostReportSerializer
)

class IsAdminOrSuperAdmin:
    """Permission class for admin/superadmin users"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type in [1, 2]

class PostPagination(PageNumberPagination):
    """Custom pagination for posts"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

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
        
        # Filter approved posts based on user type
        if user.user_type in [1, 2]:  # Admin/SuperAdmin see all approved posts
            queryset = queryset.filter(is_approved=True)
        else:  # Alumni see approved posts + their own pending posts
            queryset = queryset.filter(
                Q(is_approved=True) | Q(user=user)
            )
        
        # Apply visibility filters
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
        
        # Broadcast to admin notifications if post needs approval
        if not post.is_approved:
            async_to_sync(channel_layer.group_send)(
                'admin_notifications',
                {
                    'type': 'post_pending_approval',
                    'post_id': post.id,
                    'user': f"{user.first_name} {user.last_name}",
                    'title': post.title or post.content[:50],
                    'timestamp': post.created_at.isoformat()
                }
            )
        else:
            # Broadcast approved post to all users
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
        
        # Users can see their own posts even if not approved
        if post.user == user:
            return True
        
        # Only approved posts for other users
        if not post.is_approved:
            return False
        
        # Check visibility settings
        if post.visibility == 'admin_only' and user.user_type not in [1, 2]:
            return False
        
        return True
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

class PostReactionView(APIView):
    """Handle post reactions (Facebook-style)"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, post_id):
        """Add or update reaction to a post"""
        reaction_type = request.data.get('reaction_type')
        
        if reaction_type not in dict(Reaction.REACTION_TYPES).keys():
            return Response(
                {'error': 'Invalid reaction type'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            post = Post.objects.get(id=post_id)
            content_type = ContentType.objects.get_for_model(Post)
            
            # Get or create reaction (update if exists)
            reaction, created = Reaction.objects.update_or_create(
                user=request.user,
                content_type=content_type,
                object_id=post.id,
                defaults={'reaction_type': reaction_type}
            )
            
            # Update post reaction count
            self._update_post_reaction_count(post)
            
            # Broadcast reaction update
            self._broadcast_reaction_update(post, request.user, reaction_type, created)
            
            # Invalidate cache
            cache.delete(f"post_reactions_{post.id}")
            
            return Response({
                'success': True,
                'reaction_type': reaction_type,
                'created': created
            })
            
        except Post.DoesNotExist:
            return Response(
                {'error': 'Post not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    def delete(self, request, post_id):
        """Remove reaction from post"""
        try:
            post = Post.objects.get(id=post_id)
            content_type = ContentType.objects.get_for_model(Post)
            
            reaction = Reaction.objects.get(
                user=request.user,
                content_type=content_type,
                object_id=post.id
            )
            
            reaction_type = reaction.reaction_type
            reaction.delete()
            
            # Update post reaction count
            self._update_post_reaction_count(post)
            
            # Broadcast reaction removal
            self._broadcast_reaction_update(post, request.user, None, False, removed=True)
            
            # Invalidate cache
            cache.delete(f"post_reactions_{post.id}")
            
            return Response({'success': True, 'removed': True})
            
        except (Post.DoesNotExist, Reaction.DoesNotExist):
            return Response(
                {'error': 'Post or reaction not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    def _update_post_reaction_count(self, post):
        """Update post's likes count"""
        content_type = ContentType.objects.get_for_model(Post)
        count = Reaction.objects.filter(
            content_type=content_type,
            object_id=post.id
        ).count()
        
        post.likes_count = count
        post.save(update_fields=['likes_count'])
    
    def _broadcast_reaction_update(self, post, user, reaction_type, created, removed=False):
        """Broadcast reaction update to real-time subscribers"""
        channel_layer = get_channel_layer()
        
        async_to_sync(channel_layer.group_send)(
            f'post_{post.id}',
            {
                'type': 'reaction_update',
                'post_id': post.id,
                'user_id': user.id,
                'user_name': f"{user.first_name} {user.last_name}",
                'reaction_type': reaction_type,
                'action': 'removed' if removed else ('updated' if not created else 'added'),
                'timestamp': timezone.now().isoformat()
            }
        )

class CommentCreateView(APIView):
    """Create comments on posts"""
    permission_classes = [IsAuthenticated]
    
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
                'post': post.id,
                'content': content,
                'parent': parent_id
            }
            
            serializer = CommentSerializer(data=comment_data, context={'request': request})
            if serializer.is_valid():
                comment = serializer.save(user=request.user)
                
                # Update post comment count
                self._update_post_comment_count(post)
                
                # Broadcast new comment
                self._broadcast_new_comment(comment, request.user)
                
                # Invalidate cache
                cache.delete(f"post_comments_{post.id}")
                
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
                is_approved=True if request.user.user_type in [1, 2] else False
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

# Additional utility views for the Facebook-like features
class SavePostView(APIView):
    """Save/unsave posts"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, post_id):
        """Save a post"""
        try:
            post = Post.objects.get(id=post_id)
            saved_post, created = SavedPost.objects.get_or_create(
                user=request.user,
                post=post
            )
            
            return Response({
                'saved': True,
                'created': created
            })
            
        except Post.DoesNotExist:
            return Response(
                {'error': 'Post not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    def delete(self, request, post_id):
        """Unsave a post"""
        try:
            post = Post.objects.get(id=post_id)
            SavedPost.objects.filter(user=request.user, post=post).delete()
            
            return Response({'saved': False})
            
        except Post.DoesNotExist:
            return Response(
                {'error': 'Post not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )