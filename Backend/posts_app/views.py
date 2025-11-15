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
    PostSerializer, PostCreateSerializer, CommentSerializer, CommentCreateSerializer,
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

class PostReactionView(APIView):
    """Handle post reactions (Facebook-style)"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, post_id):
        """Get all reactions for a post"""
        try:
            post = Post.objects.get(id=post_id)
            content_type = ContentType.objects.get_for_model(Post)
            
            reactions = Reaction.objects.filter(
                content_type=content_type,
                object_id=post.id
            ).select_related('user').order_by('-created_at')
            
            serializer = ReactionSerializer(reactions, many=True, context={'request': request})
            
            return Response({
                'reactions': serializer.data,
                'total_count': reactions.count()
            })
            
        except Post.DoesNotExist:
            return Response(
                {'error': 'Post not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    def post(self, request, post_id):
        """Add or update reaction to a post"""
        try:
            print(f"DEBUG: Received reaction request - post_id: {post_id}")
            print(f"DEBUG: Request data: {request.data}")
            print(f"DEBUG: Request user: {request.user}")
            
            reaction_type = request.data.get('reaction_type')
            print(f"DEBUG: Extracted reaction_type: '{reaction_type}'")
            print(f"DEBUG: Available reaction types: {list(dict(Reaction.REACTION_TYPES).keys())}")
            
            if not reaction_type:
                return Response(
                    {'error': 'reaction_type is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if reaction_type not in dict(Reaction.REACTION_TYPES).keys():
                return Response(
                    {'error': f'Invalid reaction type: {reaction_type}. Valid types: {list(dict(Reaction.REACTION_TYPES).keys())}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            print(f"DEBUG: Error in initial validation: {e}")
            return Response(
                {'error': f'Validation error: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
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
            
            # Invalidate cache more thoroughly
            cache.delete(f"post_reactions_{post.id}")
            cache.delete(f"post_{post.id}")
            
            # Clear all post feed cache keys
            try:
                # Get all cache keys and delete feed-related ones
                if hasattr(cache, '_cache'):
                    cache_keys_to_delete = []
                    for key in cache._cache.keys():
                        if 'post_feed_' in str(key):
                            cache_keys_to_delete.append(key)
                    for key in cache_keys_to_delete:
                        cache.delete(key)
                else:
                    # Alternative approach for different cache backends
                    cache.clear()
            except Exception as e:
                print(f"DEBUG: Cache clearing error: {e}")
            
            print(f"DEBUG: Reaction {reaction_type} {'created' if created else 'updated'} for post {post_id} by user {request.user.id}")
            
            return Response({
                'success': True,
                'reaction_type': reaction_type,
                'created': created
            })
            
        except Post.DoesNotExist:
            print(f"DEBUG: Post {post_id} not found")
            return Response(
                {'error': 'Post not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"DEBUG: Unexpected error in post reaction: {e}")
            import traceback
            traceback.print_exc()
            return Response(
                {'error': f'Internal server error: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
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
        
        message_data = {
            'type': 'reaction_update',
            'post_id': post.id,
            'user_id': user.id,
            'user_name': f"{user.first_name} {user.last_name}",
            'reaction_type': reaction_type,
            'action': 'removed' if removed else ('updated' if not created else 'added'),
            'timestamp': timezone.now().isoformat()
        }
        
        # Broadcast to specific post group
        async_to_sync(channel_layer.group_send)(
            f'post_{post.id}',
            message_data
        )
        
        # Also broadcast to general posts feed for real-time updates
        async_to_sync(channel_layer.group_send)(
            'posts_feed',
            message_data
        )
        
        print(f"DEBUG: Broadcasted reaction update to WebSocket groups: post_{post.id} and posts_feed")

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

class CommentDeleteView(APIView):
    """Delete comments with Facebook-like permissions"""
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, comment_id):
        """
        Delete a comment with permission checks:
        - Comment author can delete their own comment
        - Post author can delete any comment on their post
        - Admins/SuperAdmins can delete any comment
        """
        try:
            comment = Comment.objects.select_related('user', 'post__user').get(id=comment_id)
            user = request.user
            
            # Check permissions
            can_delete = False
            deletion_reason = ""
            
            if comment.user == user:
                # User is the comment author
                can_delete = True
                deletion_reason = "comment_author"
            elif comment.post.user == user:
                # User is the post author
                can_delete = True
                deletion_reason = "post_author"
            elif user.user_type in [1, 2]:  # Admin or SuperAdmin
                can_delete = True
                deletion_reason = "admin"
            
            if not can_delete:
                return Response(
                    {
                        'error': 'Permission denied. You can only delete your own comments or comments on your posts.',
                        'code': 'COMMENT_DELETE_FORBIDDEN'
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Store post info before deletion for broadcasting
            post_id = comment.post.id
            post = comment.post
            
            # Delete comment
            comment.delete()
            
            # Update post comment count
            post.comments_count = post.comments.count()
            post.save(update_fields=['comments_count'])
            
            # Clear cache
            cache.delete(f"post_comments_{post_id}")
            cache.clear()
            
            # Broadcast comment deletion
            self._broadcast_comment_deletion(post_id, comment_id, user, deletion_reason)
            
            return Response(
                {
                    'message': 'Comment deleted successfully',
                    'deleted_by': deletion_reason,
                    'post_id': post_id,
                    'comment_id': comment_id
                },
                status=status.HTTP_200_OK
            )
            
        except Comment.DoesNotExist:
            return Response(
                {
                    'error': 'Comment not found',
                    'code': 'COMMENT_NOT_FOUND'
                },
                status=status.HTTP_404_NOT_FOUND
            )
    
    def _broadcast_comment_deletion(self, post_id, comment_id, user, deletion_reason):
        """Broadcast comment deletion to real-time subscribers"""
        channel_layer = get_channel_layer()
        
        async_to_sync(channel_layer.group_send)(
            f'post_{post_id}',
            {
                'type': 'comment_deleted',
                'post_id': post_id,
                'comment_id': comment_id,
                'deleted_by_user_id': user.id,
                'deleted_by_name': f"{user.first_name} {user.last_name}",
                'deletion_reason': deletion_reason,
                'timestamp': timezone.now().isoformat()
            }
        )
    
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


# Post Reporting Views
class PostReportView(APIView):
    """Handle post reporting functionality"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, post_id):
        """Report a post"""
        try:
            post = Post.objects.get(id=post_id)
            
            # Check if user already reported this post
            existing_report = PostReport.objects.filter(
                post=post,
                reporter=request.user
            ).first()
            
            if existing_report:
                return Response(
                    {'error': 'You have already reported this post'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get report data
            reason = request.data.get('reason')
            details = request.data.get('details', '')
            
            if not reason:
                return Response(
                    {'error': 'Report reason is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create report
            report = PostReport.objects.create(
                post=post,
                reporter=request.user,
                reason=reason,
                description=details
            )
            
            # Serialize and return
            serializer = PostReportSerializer(report)
            
            return Response({
                'message': 'Post reported successfully. Thank you for helping keep our community safe.',
                'report': serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Post.DoesNotExist:
            return Response(
                {'error': 'Post not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'An error occurred while processing your report: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminReportListView(APIView):
    """Admin view to list all post reports"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get all post reports for admin review"""
        print(f"🔍 Reports API called by user: {request.user.username if request.user.is_authenticated else 'Anonymous'}")
        print(f"🔍 User type: {getattr(request.user, 'user_type', 'None')}")
        print(f"🔍 Is authenticated: {request.user.is_authenticated}")
        
        # Check if user is admin
        if not hasattr(request.user, 'user_type') or request.user.user_type not in [1, 2]:
            print(f"❌ Access denied for user {request.user.username}: not admin")
            return Response(
                {'error': 'Admin access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        print(f"✅ Admin access granted for user {request.user.username}")
        
        try:
            # Get query parameters
            status_filter = request.query_params.get('status', 'pending')  # pending, resolved, all
            reason_filter = request.query_params.get('reason', '')
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            
            # Build queryset
            queryset = PostReport.objects.select_related('post', 'post__user', 'reporter', 'resolved_by')
            
            # Apply filters
            if status_filter == 'pending':
                queryset = queryset.filter(is_resolved=False)
            elif status_filter == 'resolved':
                queryset = queryset.filter(is_resolved=True)
            # 'all' shows everything
            
            if reason_filter:
                queryset = queryset.filter(reason=reason_filter)
            
            # Order by creation date (newest first)
            queryset = queryset.order_by('-created_at')
            
            # Pagination
            start = (page - 1) * page_size
            end = start + page_size
            reports = queryset[start:end]
            total_count = queryset.count()
            
            # Serialize data
            serializer = PostReportSerializer(reports, many=True)
            
            print(f"📊 Found {total_count} total reports, returning {len(reports)} for page {page}")
            print(f"📊 Serialized data length: {len(serializer.data)}")
            
            # Get statistics
            stats = {
                'total_reports': PostReport.objects.count(),
                'pending_reports': PostReport.objects.filter(is_resolved=False).count(),
                'resolved_today': PostReport.objects.filter(
                    is_resolved=True,
                    resolved_at__date=timezone.now().date()
                ).count(),
                'dismissed_today': PostReport.objects.filter(
                    is_resolved=True,
                    resolved_at__date=timezone.now().date(),
                    resolved_by__isnull=False
                ).count(),
            }
            
            return Response({
                'reports': serializer.data,
                'pagination': {
                    'page': page,
                    'page_size': page_size,
                    'total_count': total_count,
                    'total_pages': (total_count + page_size - 1) // page_size,
                    'has_more': end < total_count
                },
                'stats': stats
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'An error occurred while fetching reports: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
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

class AdminReportActionView(APIView):
    """Admin view to take action on post reports"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, report_id):
        """Take action on a report: dismiss, warn user, or remove post"""
        # Check if user is admin
        if not hasattr(request.user, 'user_type') or request.user.user_type not in [1, 2]:
            return Response(
                {'error': 'Admin access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            report = PostReport.objects.select_related('post', 'post__user').get(id=report_id)
            
            if report.is_resolved:
                return Response(
                    {'error': 'This report has already been resolved'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            action = request.data.get('action')
            if action not in ['dismiss', 'warn', 'remove']:
                return Response(
                    {'error': 'Invalid action. Must be one of: dismiss, warn, remove'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Mark report as resolved
            report.is_resolved = True
            report.resolved_by = request.user
            report.resolved_at = timezone.now()
            report.save()
            
            response_message = ''
            
            if action == 'dismiss':
                response_message = 'Report dismissed successfully'
                
            elif action == 'warn':
                # Here you could implement user warning system
                # For now, just mark as resolved with warning
                response_message = 'User warned and report resolved'
                
            elif action == 'remove':
                # Remove the post
                post = report.post
                post.delete()
                response_message = 'Post removed and report resolved'
            
            # Update cache version
            cache.set('posts_cache_version', cache.get('posts_cache_version', 0) + 1)
            
            return Response({
                'message': response_message,
                'action': action,
                'report_id': report_id
            }, status=status.HTTP_200_OK)
            
        except PostReport.DoesNotExist:
            return Response(
                {'error': 'Report not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'An error occurred while processing the action: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )