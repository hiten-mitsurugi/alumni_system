from rest_framework import serializers
from ..models import CustomUser
from .profile_model import ProfileModelSerializer


class UserDetailSerializer(serializers.ModelSerializer):
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