from rest_framework import serializers
from .models import Notification
from django.utils.timesince import timesince


class NotificationSerializer(serializers.ModelSerializer):
    time_ago = serializers.SerializerMethodField()
    is_read = serializers.ReadOnlyField()
    actor_name = serializers.SerializerMethodField()
    actor_avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'type', 'title', 'message', 'link_route', 'link_params',
            'metadata', 'created_at', 'read_at', 'is_read', 'time_ago',
            'actor_name', 'actor_avatar'
        ]
        read_only_fields = ['created_at', 'read_at']
    
    def get_time_ago(self, obj):
        """Human-readable time ago (e.g., '5 minutes ago')"""
        return timesince(obj.created_at) + ' ago'
    
    def get_actor_name(self, obj):
        """Get the name of the user who triggered this notification"""
        if obj.actor:
            return f"{obj.actor.first_name} {obj.actor.last_name}".strip() or obj.actor.email
        return 'System'
    
    def get_actor_avatar(self, obj):
        """Get the profile picture URL of the actor"""
        if obj.actor and hasattr(obj.actor, 'profile_picture') and obj.actor.profile_picture:
            pic = obj.actor.profile_picture
            if pic and str(pic).strip() and str(pic) != 'null':
                # Return the profile picture URL
                if pic.name.startswith('http'):
                    return pic.name
                return f'/media/{pic.name}' if not pic.name.startswith('/media/') else pic.name
        return None
