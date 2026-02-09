"""
Profile-related serializers.
Contains serializers for Profile, CustomUser details, and user search functionality.
"""
from rest_framework import serializers
from ..models import CustomUser, Profile, Following, WorkHistory
from .skills_work_serializers import WorkHistorySerializer
from .survey_serializers import (
    SkillsRelevanceSerializer, CurriculumRelevanceSerializer,
    PerceptionFurtherStudiesSerializer, FeedbackRecommendationsSerializer
)


class ProfileModelSerializer(serializers.ModelSerializer):
    """Serializer for Profile model"""
    class Meta:
        model = Profile
        exclude = ['user']


class ProfileSerializer(serializers.ModelSerializer):
    """Comprehensive profile serializer with related data"""
    work_histories = WorkHistorySerializer(many=True)
    skills_relevance = SkillsRelevanceSerializer()
    curriculum_relevance = CurriculumRelevanceSerializer()
    perception_studies = PerceptionFurtherStudiesSerializer()
    feedback = FeedbackRecommendationsSerializer()
    profile = ProfileModelSerializer()

    class Meta:
        model = CustomUser
        exclude = ['password']

    def update(self, instance, validated_data):
        from ..models import Skill, SkillsRelevance, CurriculumRelevance, PerceptionFurtherStudies, FeedbackRecommendations
        
        work_histories_data = validated_data.pop('work_histories', [])
        skills_data = validated_data.pop('skills_relevance', {})
        curriculum_data = validated_data.pop('curriculum_relevance', {})
        perception_data = validated_data.pop('perception_studies', {})
        feedback_data = validated_data.pop('feedback', {})
        profile_data = validated_data.pop('profile', {})

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        SkillsRelevance.objects.update_or_create(user=instance, defaults=skills_data)
        CurriculumRelevance.objects.update_or_create(user=instance, defaults=curriculum_data)
        PerceptionFurtherStudies.objects.update_or_create(user=instance, defaults=perception_data)
        FeedbackRecommendations.objects.update_or_create(user=instance, defaults=feedback_data)
        Profile.objects.update_or_create(user=instance, defaults=profile_data)

        instance.work_histories.all().delete()
        for wh_data in work_histories_data:
            skills = wh_data.pop('skills', [])
            work = WorkHistory.objects.create(user=instance, **wh_data)
            for skill_data in skills:
                skill_obj, _ = Skill.objects.get_or_create(**skill_data)
                work.skills.add(skill_obj)

        return instance


class UserDetailSerializer(serializers.ModelSerializer):
    """User detail serializer with profile and real-time status"""
    profile = ProfileModelSerializer(read_only=True)
    real_time_status = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = [field.name for field in CustomUser._meta.fields if field.name != 'password'] + ['profile', 'real_time_status']
    
    def get_real_time_status(self, obj):
        """Get real-time status from Redis cache first, then fallback to database"""
        try:
            from ..status_cache import UserStatusCache
            
            # First check Redis cache for real-time status
            redis_status = UserStatusCache.get_user_status(obj.id)
            redis_last_seen = UserStatusCache.get_last_seen(obj.id)
            
            # If Redis has valid status data, use it (redis_status can be 'online' or 'offline')
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


class UserSearchSerializer(serializers.ModelSerializer):
    """Serializer for user search results"""
    profile = ProfileModelSerializer(read_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'profile_picture', 'profile']


class EnhancedProfileSerializer(serializers.ModelSerializer):
    """Enhanced Profile serializer with LinkedIn-style features"""
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    connections_count = serializers.SerializerMethodField()
    posts_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    is_followed_by = serializers.SerializerMethodField()
    mutual_connection = serializers.SerializerMethodField()
    
    class Meta:
        model = Profile
        fields = '__all__'
        read_only_fields = ['user', 'timestamp']
    
    def get_followers_count(self, obj):
        return obj.get_followers_count()
    
    def get_following_count(self, obj):
        return obj.get_following_count()
    
    def get_connections_count(self, obj):
        count = obj.get_connections_count()
        print(f"🔍 Backend: get_connections_count for user {obj.user.id} = {count}")
        
        # Debug: Let's see what connections exist
        following_records = Following.objects.filter(follower=obj.user)
        follower_records = Following.objects.filter(following=obj.user)
        print(f"🔍 Backend: User {obj.user.id} is following {following_records.count()} users")
        print(f"🔍 Backend: User {obj.user.id} has {follower_records.count()} followers")
        
        for f in following_records:
            print(f"   Following: {f.following.first_name} {f.following.last_name} (status: {f.status})")
        for f in follower_records:
            print(f"   Follower: {f.follower.first_name} {f.follower.last_name} (status: {f.status})")
        
        return count
    
    def get_posts_count(self, obj):
        count = obj.get_posts_count()
        print(f"🔍 Backend: get_posts_count for user {obj.user.id} = {count}")
        return count
    
    def get_is_following(self, obj):
        """Check if current user is following this profile's user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user != obj.user:
            return Following.objects.filter(follower=request.user, following=obj.user).exists()
        return False
    
    def get_is_followed_by(self, obj):
        """Check if this profile's user is following current user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user != obj.user:
            return Following.objects.filter(follower=obj.user, following=request.user).exists()
        return False
    
    def get_mutual_connection(self, obj):
        """Check if there's a mutual connection"""
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user != obj.user:
            return Following.objects.filter(
                follower=request.user, 
                following=obj.user, 
                is_mutual=True
            ).exists()
        return False
