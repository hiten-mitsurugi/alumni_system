"""
Reaction-related views for posts_app.

This module handles reactions (likes, loves, etc.) for posts and comments.
"""

from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from ..models import Post, Comment, Reaction
from ..serializers import ReactionSerializer


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


class CommentReactionView(APIView):
    """Handle comment reactions (Facebook-style)"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, comment_id):
        """Get all reactions for a comment"""
        try:
            comment = Comment.objects.get(id=comment_id)
            content_type = ContentType.objects.get_for_model(Comment)
            
            reactions = Reaction.objects.filter(
                content_type=content_type,
                object_id=comment.id
            ).select_related('user').order_by('-created_at')
            
            serializer = ReactionSerializer(reactions, many=True, context={'request': request})
            
            return Response({
                'reactions': serializer.data,
                'total_count': reactions.count()
            })
            
        except Comment.DoesNotExist:
            return Response(
                {'error': 'Comment not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    def post(self, request, comment_id):
        """Add or update reaction to a comment"""
        try:
            print(f"DEBUG: Received comment reaction request - comment_id: {comment_id}")
            print(f"DEBUG: Request data: {request.data}")
            
            reaction_type = request.data.get('reaction_type')
            print(f"DEBUG: Extracted reaction_type: '{reaction_type}'")
            
            # Handle null reaction (remove reaction)
            if reaction_type is None or reaction_type == 'null' or reaction_type == '':
                return self._remove_reaction(request, comment_id)
            
            if reaction_type not in dict(Reaction.REACTION_TYPES).keys():
                return Response(
                    {'error': f'Invalid reaction type: {reaction_type}. Valid types: {list(dict(Reaction.REACTION_TYPES).keys())}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            print(f"DEBUG: Error in comment reaction validation: {e}")
            return Response(
                {'error': f'Validation error: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        try:
            comment = Comment.objects.get(id=comment_id)
            content_type = ContentType.objects.get_for_model(Comment)
            
            # Get or create reaction (update if exists)
            reaction, created = Reaction.objects.update_or_create(
                user=request.user,
                content_type=content_type,
                object_id=comment.id,
                defaults={'reaction_type': reaction_type}
            )
            
            # Update comment reaction count
            self._update_comment_reaction_count(comment)
            
            # Broadcast reaction update
            self._broadcast_comment_reaction(comment, reaction, request.user)
            
            action = 'created' if created else 'updated'
            
            return Response({
                'message': f'Comment reaction {action} successfully',
                'reaction_type': reaction_type,
                'emoji': reaction.emoji,
                'comment_id': comment_id
            }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
            
        except Comment.DoesNotExist:
            return Response(
                {'error': 'Comment not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    def _remove_reaction(self, request, comment_id):
        """Remove user's reaction from comment"""
        try:
            comment = Comment.objects.get(id=comment_id)
            content_type = ContentType.objects.get_for_model(Comment)
            
            reaction = Reaction.objects.filter(
                user=request.user,
                content_type=content_type,
                object_id=comment.id
            ).first()
            
            if reaction:
                reaction.delete()
                self._update_comment_reaction_count(comment)
                self._broadcast_comment_reaction(comment, None, request.user, removed=True)
                
                return Response({
                    'message': 'Comment reaction removed successfully',
                    'comment_id': comment_id
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'message': 'No reaction to remove',
                    'comment_id': comment_id
                }, status=status.HTTP_200_OK)
                
        except Comment.DoesNotExist:
            return Response(
                {'error': 'Comment not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    def _update_comment_reaction_count(self, comment):
        """Update the comment's likes count based on reactions"""
        content_type = ContentType.objects.get_for_model(Comment)
        reaction_count = Reaction.objects.filter(
            content_type=content_type,
            object_id=comment.id
        ).count()
        
        comment.likes_count = reaction_count
        comment.save(update_fields=['likes_count'])
    
    def _broadcast_comment_reaction(self, comment, reaction, user, removed=False):
        """Broadcast comment reaction update to real-time subscribers"""
        channel_layer = get_channel_layer()
        
        message = {
            'type': 'comment_reaction_updated',
            'comment_id': comment.id,
            'post_id': comment.post.id,
            'user_id': user.id,
            'user_name': f"{user.first_name} {user.last_name}",
            'timestamp': timezone.now().isoformat()
        }
        
        if removed:
            message['reaction_type'] = None
            message['action'] = 'removed'
        else:
            message['reaction_type'] = reaction.reaction_type
            message['emoji'] = reaction.emoji
            message['action'] = 'added'
        
        async_to_sync(channel_layer.group_send)(
            f'post_{comment.post.id}',
            message
        )
