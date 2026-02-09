"""
Utility views for posts_app.

This module contains miscellaneous utility views like saving posts.
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ..models import Post, SavedPost


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
