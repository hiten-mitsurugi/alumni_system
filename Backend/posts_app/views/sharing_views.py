"""
Sharing-related views for posts_app.

This module handles post sharing and reposting functionality.
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from ..models import Post
from ..serializers import PostSerializer


class PostShareView(APIView):
    """Handle post sharing with optional text"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, post_id):
        """Share a post with optional text"""
        try:
            original_post = Post.objects.get(id=post_id)
            shared_text = request.data.get('shared_text', '').strip()
            visibility = request.data.get('visibility', 'public')  # Default to public
            
            # Validate visibility choice
            valid_visibility = ['public', 'alumni_only', 'admin_only']
            if visibility not in valid_visibility:
                visibility = 'public'
            
            # Create shared post
            shared_post = Post.objects.create(
                user=request.user,
                content=shared_text or f"Shared a post by {original_post.user.first_name}",
                content_category=original_post.content_category,
                post_type='shared',
                shared_post=original_post,
                shared_text=shared_text,
                visibility=visibility,  # User's choice of privacy
                is_approved=True
            )
            
            # Update share count
            original_post.shares_count += 1
            original_post.save(update_fields=['shares_count'])
            
            # Create notification for original post author (if not sharing own post)
            if original_post.user != request.user:
                from notifications_app.utils import create_notification
                create_notification(
                    user=original_post.user,
                    actor=request.user,
                    notification_type='post',
                    title='Post Shared',
                    message=f"{request.user.first_name} {request.user.last_name} shared your post",
                    link_route='/alumni/home',
                    link_params={'postId': original_post.id},
                    metadata={'shared_post_id': shared_post.id, 'shared_text': shared_text}
                )
            
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


class PostRepostView(APIView):
    """Handle post reposting with privacy choices"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, post_id):
        """Repost a post with privacy choice"""
        try:
            original_post = Post.objects.get(id=post_id)
            repost_text = request.data.get('repost_text', '').strip()
            visibility = request.data.get('visibility', 'public')  # User's privacy choice
            
            # Validate visibility choice
            valid_visibility = ['public', 'alumni_only', 'admin_only']
            if visibility not in valid_visibility:
                visibility = 'public'
            
            # Check if user already reposted this post
            existing_repost = Post.objects.filter(
                user=request.user,
                shared_post=original_post,
                post_type='repost'
            ).first()
            
            if existing_repost:
                return Response(
                    {'error': 'You have already reposted this post'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create repost
            repost = Post.objects.create(
                user=request.user,
                content=repost_text or f"Reposted {original_post.user.first_name}'s post",
                content_category=original_post.content_category,
                post_type='repost',
                shared_post=original_post,
                shared_text=repost_text,
                visibility=visibility,  # User's choice: public, alumni_only, admin_only
                is_approved=True
            )
            
            # Update share count (repost counts as shares)
            original_post.shares_count += 1
            original_post.save(update_fields=['shares_count'])
            
            # Broadcast repost
            self._broadcast_post_repost(repost, original_post, request.user)
            
            serializer = PostSerializer(repost, context={'request': request})
            return Response({
                'message': 'Post reposted successfully',
                'repost': serializer.data,
                'visibility': visibility
            }, status=status.HTTP_201_CREATED)
            
        except Post.DoesNotExist:
            return Response(
                {'error': 'Post not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    def _broadcast_post_repost(self, repost, original_post, user):
        """Broadcast post repost to real-time subscribers"""
        channel_layer = get_channel_layer()
        
        # Notify original post author
        async_to_sync(channel_layer.group_send)(
            f'user_{original_post.user.id}',
            {
                'type': 'post_reposted',
                'original_post_id': original_post.id,
                'repost_id': repost.id,
                'reposter_id': user.id,
                'reposter_name': f"{user.first_name} {user.last_name}",
                'visibility': repost.visibility,
                'timestamp': repost.created_at.isoformat()
            }
        )
