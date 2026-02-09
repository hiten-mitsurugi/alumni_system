"""
Profile Views - User Profile Display and Management
"""
from .base_imports import *

class ProfileView(generics.RetrieveUpdateAPIView):
    """
    Get or update user profile
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    
    def get_object(self):
        user_id = self.kwargs.get('id')
        if user_id:
            return get_object_or_404(CustomUser, id=user_id)
        return self.request.user


class EnhancedProfileView(APIView):
    """
    Get enhanced user profile with additional details like:
    - Skills, Work History, Education, Achievements
    - Connection status (is_following, is_follower, is_mutual)
    - Connection counts
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id=None):
        # If user_id is provided, get that user; otherwise get current user
        if user_id:
            try:
                user = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            user = request.user
        
        # Get privacy settings
        from auth_app.models import UserFieldPrivacySettings
        privacy_settings = UserFieldPrivacySettings.objects.filter(user=user).first()
        
        # Determine viewer's relationship with the profile owner
        viewer = request.user
        is_owner = (viewer == user)
        
        # For non-owners, check visibility based on privacy settings
        if not is_owner and privacy_settings:
            # Check if viewer is a connection
            from auth_app.models import Following
            is_connection = Following.objects.filter(
                follower=viewer,
                following=user,
                status='accepted'
            ).exists()
            
            # Define visibility rules (you can customize this based on privacy_settings)
            can_view_full_profile = (
                privacy_settings.profile_visibility == 'public' or
                (privacy_settings.profile_visibility == 'connections' and is_connection)
            )
            
            if not can_view_full_profile:
                return Response({
                    'error': 'You do not have permission to view this profile',
                    'profile_visibility': privacy_settings.profile_visibility
                }, status=status.HTTP_403_FORBIDDEN)
        
        # Serialize the user
        user_data = UserDetailSerializer(user).data
        
        # Get additional profile data
        from auth_app.models import Following, Skill, WorkHistory, Education, Achievement
        
        # Connection status (only if viewing another user's profile)
        connection_status = {}
        if user != request.user:
            is_following = Following.objects.filter(
                follower=request.user,
                following=user
            ).first()
            
            is_follower = Following.objects.filter(
                follower=user,
                following=request.user
            ).first()
            
            connection_status = {
                'is_following': is_following is not None,
                'is_follower': is_follower is not None,
                'is_mutual': is_following and is_follower and is_following.status == 'accepted' and is_follower.status == 'accepted',
                'following_status': is_following.status if is_following else None,
                'follower_status': is_follower.status if is_follower else None,
                'connection_id': is_following.id if is_following else None
            }
        
        # Connection counts
        followers_count = Following.objects.filter(following=user, status='accepted').count()
        following_count = Following.objects.filter(follower=user, status='accepted').count()
        mutual_count = Following.objects.filter(following=user, is_mutual=True, status='accepted').count()
        
        # Skills
        from auth_app.serializers import SkillSerializer
        skills = Skill.objects.filter(user=user)
        skills_data = SkillSerializer(skills, many=True).data
        
        # Work History
        from auth_app.serializers import WorkHistorySerializer
        work_history = WorkHistory.objects.filter(user=user).order_by('-start_date')
        work_data = WorkHistorySerializer(work_history, many=True).data
        
        # Education
        from auth_app.serializers import EducationSerializer
        education = Education.objects.filter(user=user).order_by('-start_date')
        education_data = EducationSerializer(education, many=True).data
        
        # Achievements
        from auth_app.serializers import AchievementSerializer
        achievements = Achievement.objects.filter(user=user).order_by('-date')
        achievements_data = AchievementSerializer(achievements, many=True).data
        
        # Combine all data
        enhanced_profile = {
            **user_data,
            'connection_status': connection_status,
            'followers_count': followers_count,
            'following_count': following_count,
            'mutual_count': mutual_count,
            'skills': skills_data,
            'work_history': work_data,
            'education': education_data,
            'achievements': achievements_data,
            'is_owner': is_owner,
            'privacy_settings': {
                'profile_visibility': privacy_settings.profile_visibility if privacy_settings else 'public',
                'email_visibility': privacy_settings.email_visibility if privacy_settings else 'public',
                'skills_visibility': privacy_settings.skills_visibility if privacy_settings else 'public',
            } if privacy_settings else None
        }
        
        return Response(enhanced_profile)


class DebugEducationView(APIView):
    """Debug endpoint to see all education records and their relationships"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id):
        try:
            from auth_app.models import Education
            from auth_app.serializers import EducationSerializer
            
            # Get user
            user = CustomUser.objects.get(id=user_id)
            
            # Get all education records for this user (without ordering to see all)
            education_records = Education.objects.filter(user=user)
            
            # Serialize
            serializer = EducationSerializer(education_records, many=True)
            
            return Response({
                'user_id': user_id,
                'user_name': f"{user.first_name} {user.last_name}",
                'education_count': education_records.count(),
                'education_records': serializer.data,
                'raw_query_sql': str(education_records.query) if education_records.query else None
            })
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)
        except Exception as e:
            logger.error(f"Error in DebugEducationView: {str(e)}")
            return Response({'error': str(e)}, status=500)
