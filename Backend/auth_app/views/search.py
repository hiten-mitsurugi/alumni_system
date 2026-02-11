"""
Search and Suggestions Views - Profile Search, User Mentions, Connection Suggestions
"""
from .base_imports import *
from django.db.models import Count, Q

class ProfileSearchView(generics.ListAPIView):
    """Search for user profiles"""
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        if not query:
            return CustomUser.objects.none()
        
        return CustomUser.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query),
            is_approved=True
        ).distinct()


class SuggestedConnectionsView(APIView):
    """Get suggested connections for current user based on mutual connections and profile similarity"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        current_user = request.user
        
        from auth_app.models import Following, Skill
        
        # Get IDs of users current user is already following
        following_ids = Following.objects.filter(
            follower=current_user,
            status='accepted'
        ).values_list('following_id', flat=True)
        
        # Get IDs of pending connection requests
        pending_ids = Following.objects.filter(
            Q(follower=current_user, status='pending') | 
            Q(following=current_user, status='pending')
        ).values_list('following_id', 'follower_id')
        
        # Flatten the pending IDs (could be in either follower or following position)
        pending_user_ids = set()
        for follower_id, following_id in pending_ids:
            pending_user_ids.add(follower_id)
            pending_user_ids.add(following_id)
        
        # Remove current user from pending IDs
        pending_user_ids.discard(current_user.id)
        
        # Combine following and pending IDs
        exclude_ids = list(following_ids) + list(pending_user_ids) + [current_user.id]
        
        # Get user's skills (use UserSkill model, not Skill)
        from auth_app.models import UserSkill
        user_skills = list(UserSkill.objects.filter(user=current_user).values_list('name', flat=True))
        
        # Find users with similar skills
        suggested_users = CustomUser.objects.filter(
            is_approved=True
        ).exclude(
            id__in=exclude_ids
        ).annotate(
            mutual_count=Count('followers', filter=Q(followers__follower__in=following_ids)),
            skill_match=Count('user_skills', filter=Q(user_skills__name__in=user_skills))
        ).filter(
            Q(mutual_count__gt=0) | Q(skill_match__gt=0)
        ).order_by('-mutual_count', '-skill_match')[:10]
        
        # Serialize the suggestions
        serializer = UserDetailSerializer(suggested_users, many=True)
        
        # Add connection metadata
        suggestions = []
        for user_data in serializer.data:
            user = CustomUser.objects.get(id=user_data['id'])
            mutual_connections = Following.objects.filter(
                follower__in=following_ids,
                following=user,
                status='accepted'
            ).select_related('follower')
            
            suggestions.append({
                **user_data,
                'mutual_connections_count': mutual_connections.count(),
                'mutual_connections': [
                    {
                        'id': conn.follower.id,
                        'name': f"{conn.follower.first_name} {conn.follower.last_name}"
                    }
                    for conn in mutual_connections[:3]  # Show max 3 mutual connections
                ]
            })
        
        return Response(suggestions)


class UserByNameView(APIView):
    """Get user by exact first and last name match"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        first_name = request.query_params.get('first_name', '').strip()
        last_name = request.query_params.get('last_name', '').strip()
        
        if not first_name or not last_name:
            return Response({'error': 'Both first_name and last_name are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        users = CustomUser.objects.filter(
            first_name__iexact=first_name,
            last_name__iexact=last_name,
            is_approved=True
        )
        
        serializer = UserDetailSerializer(users, many=True)
        return Response(serializer.data)


class UserMentionSearchView(APIView):
    """Search users for @ mentions (quick search by name)"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        query = request.query_params.get('q', '').strip()
        
        if len(query) < 2:
            return Response({'users': []})
        
        # Search by first name, last name, or full name
        users = CustomUser.objects.filter(
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query) |
            Q(email__icontains=query),
            is_approved=True
        ).distinct()[:10]  # Limit to 10 results
        
        # Return minimal user data for mentions
        results = [{
            'id': user.id,
            'name': f"{user.first_name} {user.last_name}",
            'email': user.email,
            'profile_picture': user.profile_picture.url if user.profile_picture else None
        } for user in users]
        
        return Response({'users': results})
