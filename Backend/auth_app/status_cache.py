"""
Redis-based status caching for real-time user status tracking
"""
import json
from datetime import datetime, timedelta
from django.core.cache import cache
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import redis
from django.conf import settings

# Redis connection for direct operations
try:
    if settings.REDIS_PASSWORD:
        redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
    else:
        redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0, decode_responses=True)
except Exception as e:
    print(f"Redis connection error: {e}")
    redis_client = None

class UserStatusCache:
    """Manages user online/offline status in Redis cache"""
    
    ONLINE_USERS_KEY = "online_users"
    USER_STATUS_PREFIX = "user_status:"
    USER_LAST_SEEN_PREFIX = "user_last_seen:"
    STATUS_EXPIRY = 300  # 5 minutes
    
    @classmethod
    def set_user_online(cls, user_id):
        """Mark user as online"""
        if not redis_client:
            print("Redis client not available, skipping status cache update")
            return
            
        try:
            # Add to online users set
            redis_client.sadd(cls.ONLINE_USERS_KEY, user_id)
            
            # Set individual status with expiry
            redis_client.setex(
                f"{cls.USER_STATUS_PREFIX}{user_id}",
                cls.STATUS_EXPIRY,
                "online"
            )
            
            # Update last seen
            cls.update_last_seen(user_id)
            
            # Update database profile status to online
            try:
                from auth_app.models import Alumni
                alumni = Alumni.objects.get(id=user_id)
                if hasattr(alumni, 'profile') and alumni.profile:
                    alumni.profile.status = 'online'
                    alumni.profile.last_seen = timezone.now()
                    alumni.profile.save(update_fields=['status', 'last_seen'])
                    print(f"Updated database profile for user {user_id} to online")
            except Exception as db_error:
                print(f"Error updating database profile for user {user_id}: {db_error}")
            
            # Broadcast status change
            cls.broadcast_status_change(user_id, "online")
            
        except Exception as e:
            print(f"Error setting user {user_id} online: {e}")
    
    @classmethod
    def set_user_offline(cls, user_id):
        """Mark user as offline"""
        if not redis_client:
            print("Redis client not available, skipping status cache update")
            return
            
        try:
            # Remove from online users set
            redis_client.srem(cls.ONLINE_USERS_KEY, user_id)
            
            # Set status as offline
            redis_client.setex(
                f"{cls.USER_STATUS_PREFIX}{user_id}",
                cls.STATUS_EXPIRY * 4,  # Keep offline status longer
                "offline"
            )
            
            # Update last seen
            cls.update_last_seen(user_id)
            
            # Update database profile status to offline
            try:
                from auth_app.models import Alumni
                alumni = Alumni.objects.get(id=user_id)
                if hasattr(alumni, 'profile') and alumni.profile:
                    alumni.profile.status = 'offline'
                    alumni.profile.last_seen = timezone.now()
                    alumni.profile.save(update_fields=['status', 'last_seen'])
                    print(f"Updated database profile for user {user_id} to offline")
            except Exception as db_error:
                print(f"Error updating database profile for user {user_id}: {db_error}")
            
            # Broadcast status change
            cls.broadcast_status_change(user_id, "offline")
            
        except Exception as e:
            print(f"Error setting user {user_id} offline: {e}")
    
    @classmethod
    def get_user_status(cls, user_id):
        """Get user's current status"""
        if not redis_client:
            return "offline"
            
        try:
            # Check individual status first
            status = redis_client.get(f"{cls.USER_STATUS_PREFIX}{user_id}")
            if status:
                return status
            
            # If no individual status, the user is offline
            # Remove from online set if present (cleanup expired status)
            if redis_client.sismember(cls.ONLINE_USERS_KEY, user_id):
                redis_client.srem(cls.ONLINE_USERS_KEY, user_id)
                print(f"Cleaned up expired online status for user {user_id}")
            
            return "offline"
            
        except Exception as e:
            print(f"Error getting status for user {user_id}: {e}")
            return "offline"
    
    @classmethod
    def update_last_seen(cls, user_id):
        """Update user's last seen timestamp"""
        if not redis_client:
            return
            
        try:
            timestamp = timezone.now().isoformat()
            redis_client.setex(
                f"{cls.USER_LAST_SEEN_PREFIX}{user_id}",
                86400,  # 24 hours
                timestamp
            )
        except Exception as e:
            print(f"Error updating last seen for user {user_id}: {e}")
    
    @classmethod
    def get_last_seen(cls, user_id):
        """Get user's last seen timestamp"""
        if not redis_client:
            return None
            
        try:
            timestamp_str = redis_client.get(f"{cls.USER_LAST_SEEN_PREFIX}{user_id}")
            if timestamp_str:
                return datetime.fromisoformat(timestamp_str)
            return None
        except Exception as e:
            print(f"Error getting last seen for user {user_id}: {e}")
            return None
    
    @classmethod
    def get_online_users(cls):
        """Get list of currently online users"""
        if not redis_client:
            return []
            
        try:
            return [int(user_id) for user_id in redis_client.smembers(cls.ONLINE_USERS_KEY)]
        except Exception as e:
            print(f"Error getting online users: {e}")
            return []
    
    @classmethod
    def cleanup_offline_users(cls):
        """Remove users who haven't been seen for a while"""
        if not redis_client:
            return
            
        try:
            cutoff_time = timezone.now() - timedelta(minutes=10)
            online_users = redis_client.smembers(cls.ONLINE_USERS_KEY)
            
            for user_id in online_users:
                last_seen = cls.get_last_seen(user_id)
                if last_seen and last_seen < cutoff_time:
                    cls.set_user_offline(user_id)
                    
        except Exception as e:
            print(f"Error cleaning up offline users: {e}")
    
    @classmethod
    def broadcast_status_change(cls, user_id, status):
        """Broadcast status change to all connected clients"""
        try:
            channel_layer = get_channel_layer()
            message = {
                'type': 'status_update',
                'data': {
                    'user_id': user_id,
                    'status': status,
                    'timestamp': timezone.now().isoformat()
                }
            }
            
            # Broadcast to management group
            async_to_sync(channel_layer.group_send)(
                'user_management',
                {
                    'type': 'broadcast_message',
                    'message': message
                }
            )
            
            # Also broadcast to status updates group for backward compatibility
            async_to_sync(channel_layer.group_send)(
                'status_updates',
                message
            )
            
        except Exception as e:
            print(f"Error broadcasting status change for user {user_id}: {e}")
    
    @classmethod
    def refresh_user_activity(cls, user_id):
        """Refresh user activity (call on each action)"""
        try:
            current_status = cls.get_user_status(user_id)
            if current_status == "offline":
                cls.set_user_online(user_id)
            else:
                # Just update last seen and extend online status
                cls.update_last_seen(user_id)
                redis_client.expire(f"{cls.USER_STATUS_PREFIX}{user_id}", cls.STATUS_EXPIRY)
                
        except Exception as e:
            print(f"Error refreshing activity for user {user_id}: {e}")

# Utility functions for easy access
def set_user_online(user_id):
    """Convenience function to set user online"""
    UserStatusCache.set_user_online(user_id)

def set_user_offline(user_id):
    """Convenience function to set user offline"""
    UserStatusCache.set_user_offline(user_id)

def get_user_status(user_id):
    """Convenience function to get user status"""
    return UserStatusCache.get_user_status(user_id)

def refresh_user_activity(user_id):
    """Convenience function to refresh user activity"""
    UserStatusCache.refresh_user_activity(user_id)
