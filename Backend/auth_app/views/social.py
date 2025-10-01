from .base import *


class FollowUserView(APIView):
    """Follow/unfollow another user"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, user_id):
        try:
            target_user = CustomUser.objects.get(id=user_id, is_approved=True)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if target_user == request.user:
            return Response({'error': 'Cannot follow yourself'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if already following
        follow_relationship, created = Follow.objects.get_or_create(
            follower=request.user,
            following=target_user
        )
        
        if created:
            return Response({'status': 'followed'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'status': 'already_following'}, status=status.HTTP_200_OK)
    
    def delete(self, request, user_id):
        try:
            target_user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            follow_relationship = Follow.objects.get(
                follower=request.user,
                following=target_user
            )
            follow_relationship.delete()
            return Response({'status': 'unfollowed'}, status=status.HTTP_200_OK)
        except Follow.DoesNotExist:
            return Response({'error': 'Not following this user'}, status=status.HTTP_400_BAD_REQUEST)


class UserConnectionsView(APIView):
    """Get user's followers and following"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id=None):
        user = get_object_or_404(CustomUser, id=user_id) if user_id else request.user
        connection_type = request.query_params.get('type', 'followers')
        
        if connection_type == 'followers':
            connections = Follow.objects.filter(following=user).select_related('follower')
            users = [f.follower for f in connections]
        elif connection_type == 'following':
            connections = Follow.objects.filter(follower=user).select_related('following')
            users = [f.following for f in connections]
        else:
            return Response({'error': 'Invalid connection type'}, status=status.HTTP_400_BAD_REQUEST)
        
        from ..serializers import UserDetailSerializer
        serializer = UserDetailSerializer(users, many=True, context={'request': request})
        return Response(serializer.data)


class NetworkSuggestionsView(APIView):
    """Get network connection suggestions"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Get users from same program/year (exclude current user and already following)
        following_ids = Follow.objects.filter(follower=user).values_list('following_id', flat=True)
        suggestions = CustomUser.objects.filter(
            user_type=3,  # Alumni
            is_approved=True,
            program=user.program,
            year_graduated=user.year_graduated
        ).exclude(
            id__in=list(following_ids) + [user.id]
        )[:10]
        
        from ..serializers import UserDetailSerializer
        serializer = UserDetailSerializer(suggestions, many=True, context={'request': request})
        return Response(serializer.data)


class UserActivityView(APIView):
    """Get user's activity feed"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id=None):
        target_user = get_object_or_404(CustomUser, id=user_id) if user_id else request.user
        
        # Get recent posts from this user
        from posts_app.models import Post
        posts = Post.objects.filter(author=target_user).order_by('-created_at')[:20]
        
        # Format activity data
        activities = []
        for post in posts:
            activities.append({
                'type': 'post',
                'id': post.id,
                'content': post.content[:200],
                'created_at': post.created_at,
                'likes_count': post.likes.count(),
                'comments_count': post.comments.count()
            })
        
        return Response({
            'user_id': target_user.id,
            'activities': activities
        })