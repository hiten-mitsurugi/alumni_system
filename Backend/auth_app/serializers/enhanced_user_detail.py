from rest_framework import serializers
from ..models import CustomUser
from .enhanced_profile import EnhancedProfileSerializer
from .work_history import WorkHistorySerializer
from .achievement import AchievementSerializer
from .education import EducationSerializer


class EnhancedUserDetailSerializer(serializers.ModelSerializer):
    """Enhanced User serializer with LinkedIn-style profile features"""
    profile = EnhancedProfileSerializer(read_only=True)
    work_histories = WorkHistorySerializer(many=True, read_only=True)
    achievements = AchievementSerializer(many=True, read_only=True)
    education = EducationSerializer(many=True, read_only=True)
    real_time_status = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = [field.name for field in CustomUser._meta.fields if field.name != 'password'] + [
            'profile', 'work_histories', 'achievements', 'education', 'real_time_status'
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