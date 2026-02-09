"""
Enhanced user detail serializer with privacy enforcement.
Contains EnhancedUserDetailSerializer with comprehensive privacy logic.
"""
from rest_framework import serializers
from django.db.models import Q
from ..models import CustomUser, Following
from .profile_serializers import EnhancedProfileSerializer
from .skills_work_serializers import WorkHistorySerializer, UserSkillSerializer
from .profile_items_serializers import (
    AchievementSerializer, EducationSerializer, MembershipSerializer,
    RecognitionSerializer, TrainingSerializer, PublicationSerializer,
    CertificateSerializer, CSEStatusSerializer
)


class EnhancedUserDetailSerializer(serializers.ModelSerializer):
    """Enhanced User serializer with LinkedIn-style profile features"""
    profile = EnhancedProfileSerializer(read_only=True)
    work_histories = serializers.SerializerMethodField()
    achievements = AchievementSerializer(many=True, read_only=True)
    education = serializers.SerializerMethodField()
    user_skills = UserSkillSerializer(many=True, read_only=True)
    memberships = MembershipSerializer(many=True, read_only=True)
    recognitions = RecognitionSerializer(many=True, read_only=True)
    trainings = TrainingSerializer(many=True, read_only=True)
    publications = PublicationSerializer(many=True, read_only=True)
    certificates = CertificateSerializer(many=True, read_only=True)
    cse_status = CSEStatusSerializer(read_only=True)
    real_time_status = serializers.SerializerMethodField()
    
    def get_work_histories(self, obj):
        """Get work histories for the user"""
        work_histories = obj.work_histories.all()
        return WorkHistorySerializer(work_histories, many=True).data
    
    def get_education(self, obj):
        """Explicitly get education records for the user"""
        try:
            from ..models import Education
            education_records = Education.objects.filter(user=obj)
            print(f"🔍 DEBUG get_education: Found {education_records.count()} records for user {obj.id}")
            
            if education_records.exists():
                for edu in education_records:
                    print(f"  📚 {edu.field_of_study} at {edu.institution}")
                
                # Use the EducationSerializer defined in this file
                serialized_data = EducationSerializer(education_records, many=True).data
                print(f"🔍 Serialized education data: {serialized_data}")
                return serialized_data
            else:
                print(f"🔍 No education records found for user {obj.id}")
                return []
        except Exception as e:
            print(f"❌ Error in get_education: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def to_representation(self, instance):
        """Override to filter data based on privacy settings"""
        ret = super().to_representation(instance)
        
        # Get the requesting user from context
        request = self.context.get('request')
        requesting_user = request.user if request else None
        
        # If this is the user's own profile, return everything
        if requesting_user and requesting_user.id == instance.id:
            print(f"🔓 Own profile - returning all data for user {instance.id}")
            return ret
        
        # PROFILE-LEVEL PRIVACY CHECK (NEW)
        # Check profile_visibility BEFORE applying per-field filters
        profile_visibility = 'public'  # default
        if hasattr(instance, 'profile') and instance.profile:
            profile_visibility = instance.profile.profile_visibility
        
        print(f"🔒 Profile visibility: {profile_visibility} for user {instance.id}, viewed by {requesting_user.id if requesting_user else 'anonymous'}")
        
        # If profile is PRIVATE and viewer is not the owner, return minimal card
        if profile_visibility == 'private':
            print(f"🚫 PRIVATE profile - returning minimal card")
            return self._get_minimal_profile_card(instance, 'private')
        
        # If profile is CONNECTIONS_ONLY, check if viewer is connected
        if profile_visibility == 'connections_only':
            if not requesting_user or requesting_user.is_anonymous:
                print(f"🚫 CONNECTIONS_ONLY profile - viewer not authenticated, returning minimal card")
                return self._get_minimal_profile_card(instance, 'connections_only')
            
            # Check if viewer is connected to profile owner
            is_connected = self._is_user_connected(requesting_user, instance)
            if not is_connected:
                print(f"🚫 CONNECTIONS_ONLY profile - viewer not connected, returning minimal card")
                return self._get_minimal_profile_card(instance, 'connections_only')
            else:
                print(f"✅ CONNECTIONS_ONLY profile - viewer IS connected, showing full profile")
        
        # Profile is PUBLIC or viewer is authorized -> Apply per-field privacy filtering
        print(f"🔒 Filtering per-field privacy for user {instance.id}")
        ret = self._filter_privacy_items(ret, instance, requesting_user)
        
        return ret
    
    def _is_user_connected(self, requesting_user, target_user):
        """
        Check if requesting_user is connected to target_user.
        Connection = accepted Following relationship with is_mutual=True in either direction
        """
        # Check if users are connected (either direction with is_mutual and accepted status)
        connection_exists = Following.objects.filter(
            Q(follower=requesting_user, following=target_user) | 
            Q(follower=target_user, following=requesting_user),
            is_mutual=True,
            status='accepted'
        ).exists()
        
        print(f"🔍 Connection check: {requesting_user.username} ↔ {target_user.username} = {connection_exists}")
        return connection_exists
    
    def _get_minimal_profile_card(self, instance, visibility_type):
        """
        Return a minimal profile card when full profile is not accessible.
        Includes only basic public info + a flag indicating why it's restricted.
        """
        return {
            'id': instance.id,
            'username': instance.username,
            'first_name': instance.first_name,
            'last_name': instance.last_name,
            'profile_picture': instance.profile_picture.url if instance.profile_picture else None,
            'is_restricted': True,
            'restriction_reason': visibility_type,  # 'private' or 'connections_only'
            'message': 'This profile is private' if visibility_type == 'private' 
                      else 'This profile is only visible to connections',
            'profile': {
                'profile_visibility': visibility_type
            } if hasattr(instance, 'profile') and instance.profile else None
        }
    
    def _filter_privacy_items(self, data, target_user, requesting_user):
        """Filter individual items based on their privacy settings"""
        from ..models import FieldPrivacySetting
        
        # Filter education items
        if 'education' in data and data['education']:
            filtered_education = []
            for edu in data['education']:
                field_name = f"education_{edu['id']}"
                visibility = FieldPrivacySetting.get_user_field_visibility(target_user, field_name)
                if self._is_item_visible(visibility, requesting_user, target_user):
                    filtered_education.append(edu)
                else:
                    print(f"🚫 Hiding education {edu['id']} (visibility: {visibility})")
            data['education'] = filtered_education
        
        # Filter work histories
        if 'work_histories' in data and data['work_histories']:
            filtered_work = []
            for work in data['work_histories']:
                field_name = f"experience_{work['id']}"
                visibility = FieldPrivacySetting.get_user_field_visibility(target_user, field_name)
                if self._is_item_visible(visibility, requesting_user, target_user):
                    filtered_work.append(work)
                else:
                    print(f"🚫 Hiding work experience {work['id']} (visibility: {visibility})")
            data['work_histories'] = filtered_work
        
        # Filter achievements
        if 'achievements' in data and data['achievements']:
            filtered_achievements = []
            for achievement in data['achievements']:
                field_name = f"achievement_{achievement['id']}"
                visibility = FieldPrivacySetting.get_user_field_visibility(target_user, field_name)
                if self._is_item_visible(visibility, requesting_user, target_user):
                    filtered_achievements.append(achievement)
                else:
                    print(f"🚫 Hiding achievement {achievement['id']} (visibility: {visibility})")
            data['achievements'] = filtered_achievements
        
        # Filter user skills
        if 'user_skills' in data and data['user_skills']:
            filtered_skills = []
            for skill in data['user_skills']:
                field_name = f"skill_{skill['id']}"
                visibility = FieldPrivacySetting.get_user_field_visibility(target_user, field_name)
                if self._is_item_visible(visibility, requesting_user, target_user):
                    filtered_skills.append(skill)
                else:
                    print(f"🚫 Hiding skill {skill['id']} (visibility: {visibility})")
            data['user_skills'] = filtered_skills
        
        # Filter memberships
        if 'memberships' in data and data['memberships']:
            filtered_memberships = []
            for membership in data['memberships']:
                field_name = f"membership_{membership['id']}"
                visibility = FieldPrivacySetting.get_user_field_visibility(target_user, field_name)
                if self._is_item_visible(visibility, requesting_user, target_user):
                    filtered_memberships.append(membership)
                else:
                    print(f"🚫 Hiding membership {membership['id']} (visibility: {visibility})")
            data['memberships'] = filtered_memberships
        
        # Filter recognitions
        if 'recognitions' in data and data['recognitions']:
            filtered_recognitions = []
            for recognition in data['recognitions']:
                field_name = f"recognition_{recognition['id']}"
                visibility = FieldPrivacySetting.get_user_field_visibility(target_user, field_name)
                if self._is_item_visible(visibility, requesting_user, target_user):
                    filtered_recognitions.append(recognition)
                else:
                    print(f"🚫 Hiding recognition {recognition['id']} (visibility: {visibility})")
            data['recognitions'] = filtered_recognitions
        
        # Filter trainings
        if 'trainings' in data and data['trainings']:
            filtered_trainings = []
            for training in data['trainings']:
                field_name = f"training_{training['id']}"
                visibility = FieldPrivacySetting.get_user_field_visibility(target_user, field_name)
                if self._is_item_visible(visibility, requesting_user, target_user):
                    filtered_trainings.append(training)
                else:
                    print(f"🚫 Hiding training {training['id']} (visibility: {visibility})")
            data['trainings'] = filtered_trainings
        
        # Filter publications
        if 'publications' in data and data['publications']:
            filtered_publications = []
            for publication in data['publications']:
                field_name = f"publication_{publication['id']}"
                visibility = FieldPrivacySetting.get_user_field_visibility(target_user, field_name)
                if self._is_item_visible(visibility, requesting_user, target_user):
                    filtered_publications.append(publication)
                else:
                    print(f"🚫 Hiding publication {publication['id']} (visibility: {visibility})")
            data['publications'] = filtered_publications
        
        # Filter certificates
        if 'certificates' in data and data['certificates']:
            filtered_certificates = []
            for certificate in data['certificates']:
                field_name = f"certificate_{certificate['id']}"
                visibility = FieldPrivacySetting.get_user_field_visibility(target_user, field_name)
                if self._is_item_visible(visibility, requesting_user, target_user):
                    filtered_certificates.append(certificate)
                else:
                    print(f"🚫 Hiding certificate {certificate['id']} (visibility: {visibility})")
            data['certificates'] = filtered_certificates
        
        # Filter CSE status
        if 'cse_status' in data and data['cse_status']:
            field_name = "cse_status"
            visibility = FieldPrivacySetting.get_user_field_visibility(target_user, field_name)
            if not self._is_item_visible(visibility, requesting_user, target_user):
                print(f"🚫 Hiding CSE status (visibility: {visibility})")
                data['cse_status'] = None
        
        return data
    
    def _is_item_visible(self, visibility, requesting_user, target_user):
        """Check if an item should be visible based on privacy settings"""
        print(f"🔍 _is_item_visible: visibility={visibility}, requesting_user={requesting_user.id if requesting_user else None}, target_user={target_user.id}")
        
        if visibility == 'everyone':
            print(f"✅ Visible to everyone")
            return True
        elif visibility == 'only_me':
            print(f"🚫 Visible only to owner")
            return False
        elif visibility == 'connections_only':
            if not requesting_user or requesting_user.is_anonymous:
                print(f"🚫 Not visible - user not authenticated")
                return False
            
            # Check if users are connected (mutual connection)
            # Check both directions for mutual connection
            connection_exists = Following.objects.filter(
                follower=requesting_user,
                following=target_user,
                is_mutual=True,
                status='accepted'
            ).exists()
            
            print(f"🔍 Checking connection: {requesting_user.username} → {target_user.username}")
            print(f"🔍 Connection exists (is_mutual=True, status=accepted): {connection_exists}")
            
            if not connection_exists:
                # Also check reverse direction
                reverse_connection = Following.objects.filter(
                    follower=target_user,
                    following=requesting_user,
                    is_mutual=True,
                    status='accepted'
                ).exists()
                print(f"🔍 Reverse connection: {target_user.username} → {requesting_user.username}: {reverse_connection}")
                connection_exists = reverse_connection
            
            # Debug: Show all connections for these users
            all_connections_from_requester = Following.objects.filter(follower=requesting_user)
            all_connections_to_target = Following.objects.filter(following=target_user)
            print(f"📊 All connections FROM {requesting_user.username}: {list(all_connections_from_requester.values('following__username', 'is_mutual', 'status'))}")
            print(f"📊 All connections TO {target_user.username}: {list(all_connections_to_target.values('follower__username', 'is_mutual', 'status'))}")
            
            return connection_exists
        
        print(f"⚠️ Unknown visibility: {visibility}")
        return False
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'middle_name',
            'user_type', 'sex', 'gender', 'civil_status', 'employment_status',
            'is_approved', 'profile_picture', 'government_id', 'program',
            'contact_number', 'birth_date', 'year_graduated', 'mothers_name',
            'mothers_occupation', 'fathers_name', 'fathers_occupation',
            'is_active', 'is_staff', 'is_superuser', 'last_login', 'date_joined',
            'profile', 'work_histories', 'achievements', 'education', 'user_skills',
            'memberships', 'recognitions', 'trainings', 'publications', 'certificates',
            'cse_status', 'real_time_status'
        ]
    
    def get_real_time_status(self, obj):
        """Get real-time status from Redis cache first, then fallback to database"""
        try:
            from ..status_cache import UserStatusCache
            
            # First check Redis cache for real-time status
            redis_status = UserStatusCache.get_user_status(obj.id)
            redis_last_seen = UserStatusCache.get_last_seen(obj.id)
            
            # If Redis has valid status data, use it
            if redis_status and redis_status in ['online', 'offline']:
                return {
                    'status': redis_status,
                    'last_seen': redis_last_seen.isoformat() if redis_last_seen else None,
                    'is_online': redis_status == 'online'
                }
            
            # Fallback to database profile status
            if hasattr(obj, 'profile') and obj.profile:
                return {
                    'status': obj.profile.status,
                    'last_seen': obj.profile.last_seen.isoformat() if obj.profile.last_seen else None,
                    'is_online': obj.profile.status == 'online'
                }
            else:
                return {
                    'status': 'offline',
                    'last_seen': None,
                    'is_online': False
                }
        except Exception as e:
            # Fallback to offline status if there's any error
            return {
                'status': 'offline',
                'last_seen': None,
                'is_online': False
            }
