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
        
        from auth_app.models import Following
        
        # Debug logging
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"🔍 Suggestions requested for user {current_user.id} ({current_user.username})")
        
        # Get IDs of users current user is already following (accepted connections)
        following_ids = Following.objects.filter(
            follower=current_user,
            status='accepted'
        ).values_list('following_id', flat=True)
        
        logger.info(f"🔍 User has {len(following_ids)} accepted connections (following)")
        
        # Get IDs of users who are following the current user (followers with accepted status)
        follower_ids = Following.objects.filter(
            following=current_user,
            status='accepted'
        ).values_list('follower_id', flat=True)
        
        logger.info(f"🔍 User has {len(follower_ids)} followers (accepted)")
        
        # Get IDs of pending connection requests (in either direction)
        pending_ids = Following.objects.filter(
            Q(follower=current_user, status='pending') | 
            Q(following=current_user, status='pending')
        ).values_list('following_id', 'follower_id')
        
        # Flatten the pending IDs
        pending_user_ids = set()
        for follower_id, following_id in pending_ids:
            pending_user_ids.add(follower_id)
            pending_user_ids.add(following_id)
        pending_user_ids.discard(current_user.id)
        
        logger.info(f"🔍 Found {len(pending_user_ids)} pending connections")
        
        # Combine following, follower, and pending IDs
        exclude_ids = list(following_ids) + list(follower_ids) + list(pending_user_ids) + [current_user.id]
        
        logger.info(f"🔍 Excluding {len(exclude_ids)} users total")
        
        # Get user's skills for matching
        from auth_app.models import UserSkill
        user_skills = list(UserSkill.objects.filter(user=current_user).values_list('name', flat=True))
        
        logger.info(f"🔍 Current user has {len(user_skills)} skills")
        
        # Base query: All approved, active alumni except excluded users
        base_queryset = CustomUser.objects.filter(
            user_type=3,  # Alumni only
            is_approved=True,
            is_active=True
        ).exclude(id__in=exclude_ids)
        
        logger.info(f"🔍 Found {base_queryset.count()} potential suggestions after exclusions")
        
        # Get user's skills for matching
        from auth_app.models import UserSkill
        user_skills = list(UserSkill.objects.filter(user=current_user).values_list('name', flat=True))
        
        logger.info(f"🔍 Current user has {len(user_skills)} skills")
        
        # Convert base_queryset to list to work with
        all_candidates = list(base_queryset)
        
        logger.info(f"🔍 Total candidates available: {len(all_candidates)}")
        
        # If we have candidates, prioritize by mutual connections and skills
        if all_candidates and (following_ids or user_skills):
            # Try to find users with mutual connections or skill matches
            prioritized = []
            regular = []
            
            for candidate in all_candidates:
                # Count mutual connections
                mutual_count = Following.objects.filter(
                    follower__in=following_ids,
                    following=candidate,
                    status='accepted'
                ).count() if following_ids else 0
                
                # Count skill matches
                skill_count = UserSkill.objects.filter(
                    user=candidate,
                    name__in=user_skills
                ).count() if user_skills else 0
                
                if mutual_count > 0 or skill_count > 0:
                    prioritized.append((candidate, mutual_count, skill_count))
                else:
                    regular.append((candidate, 0, 0))
            
            # Sort prioritized by mutual count, then skill count
            prioritized.sort(key=lambda x: (x[1], x[2]), reverse=True)
            
            # Combine: prioritized first, then regular
            all_sorted = prioritized + regular
            suggested_users = [user[0] for user in all_sorted[:10]]
            
            logger.info(f"🔍 Prioritized {len(prioritized)} users, {len(regular)} regular")
        else:
            # No following or skills, just return all candidates
            suggested_users = all_candidates[:10]
            logger.info(f"🔍 No prioritization possible, returning {len(suggested_users)} users")
        
        logger.info(f"🔍 Final count: {len(suggested_users)} suggestions")
        
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
                'mutual_connections': mutual_connections.count(),
                'mutual_connections_list': [
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
