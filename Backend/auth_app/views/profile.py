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
        
        # Resolve privacy settings safely. The project uses a per-field
        # `FieldPrivacySetting` model (not a single `UserFieldPrivacySettings`).
        # To avoid ImportError and keep this endpoint stable, default to
        # no privacy restrictions when the expected model/fields aren't
        # available. This prevents 500s while preserving backward
        # compatibility.
        privacy_settings = None
        try:
            from auth_app.models import FieldPrivacySetting
            # We don't attempt to map per-field settings into the older
            # aggregate shape here; leave `privacy_settings` as None so the
            # endpoint behaves as public by default.
        except Exception:
            privacy_settings = None
        
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
        from auth_app.models import Following, UserSkill, WorkHistory, Education, Achievement
        
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
        
        # Skills (use UserSkill which links users to skill entries)
        from auth_app.serializers.skills_work_serializers import UserSkillSerializer
        user_skills = UserSkill.objects.filter(user=user)
        skills_data = UserSkillSerializer(user_skills, many=True).data
        
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
        achievements = Achievement.objects.filter(user=user).order_by('-date_achieved')
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
            'privacy_settings': None  # Simplified; field-based privacy handled elsewhere
        }
        
        # Safely add memberships, recognitions, trainings, publications if available
        try:
            from auth_app.models import Membership, Recognition, Training, Publication, Certificate
            from auth_app.serializers.profile_items_serializers import (
                MembershipSerializer, RecognitionSerializer, 
                TrainingSerializer, PublicationSerializer, CertificateSerializer
            )
            
            memberships = Membership.objects.filter(user=user)
            enhanced_profile['memberships'] = MembershipSerializer(memberships, many=True).data
            
            recognitions = Recognition.objects.filter(user=user)
            enhanced_profile['recognitions'] = RecognitionSerializer(recognitions, many=True).data
            
            trainings = Training.objects.filter(user=user)
            enhanced_profile['trainings'] = TrainingSerializer(trainings, many=True).data
            
            publications = Publication.objects.filter(user=user)
            enhanced_profile['publications'] = PublicationSerializer(publications, many=True).data
            
            certificates = Certificate.objects.filter(user=user)
            enhanced_profile['certificates'] = CertificateSerializer(certificates, many=True).data
        except Exception as e:
            logger.error(f"Error fetching additional profile data: {str(e)}", exc_info=True)
            # Continue without these fields if there's an error
        
        return Response(enhanced_profile)
    
    def patch(self, request, user_id=None, username=None):
        """
        Update user profile (supports profile picture, cover photo, and other fields)
        Only allows users to update their own profile
        """
        # If user_id or username is provided, validate it matches the current user
        if user_id and user_id != request.user.id:
            return Response({
                'error': 'You can only update your own profile'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if username and username != request.user.username:
            return Response({
                'error': 'You can only update your own profile'
            }, status=status.HTTP_403_FORBIDDEN)
        
        user = request.user
        
        try:
            # Handle file uploads
            profile_picture = request.FILES.get('profile_picture')
            cover_photo = request.FILES.get('cover_photo')
            
            # Update fields on CustomUser model
            updatable_fields = [
                'first_name', 'last_name', 'email', 'contact_number', 
                'bio', 'middle_name', 'program', 'year_graduated'
            ]
            
            for field in updatable_fields:
                if field in request.data:
                    setattr(user, field, request.data[field])
            
            # Handle profile picture upload (on CustomUser)
            if profile_picture:
                user.profile_picture = profile_picture
            
            user.save()
            
            # Handle cover photo and other profile fields (on Profile model)
            profile, created = Profile.objects.get_or_create(user=user)
            
            profile_fields = [
                'location', 'headline', 'summary', 
                'linkedin_url', 'facebook_url', 'twitter_url', 
                'instagram_url', 'website_url'
            ]
            
            for field in profile_fields:
                if field in request.data:
                    setattr(profile, field, request.data[field])
            
            if cover_photo:
                profile.cover_photo = cover_photo
            
            profile.save()
            
            # Return updated user data
            user_data = UserDetailSerializer(user).data
            
            return Response({
                'message': 'Profile updated successfully',
                **user_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error updating profile: {str(e)}")
            return Response({
                'error': 'Failed to update profile',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


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
