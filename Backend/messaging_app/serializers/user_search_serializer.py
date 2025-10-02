from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import BlockedUser
from .user_profile_serializer import UserProfileSerializer


CustomUser = get_user_model()


class UserSearchSerializer(serializers.ModelSerializer):
    """User Search Serializer (includes profile info)"""
    profile_picture = serializers.SerializerMethodField()
    profile = UserProfileSerializer(read_only=True)
    is_blocked_by_me = serializers.SerializerMethodField()
    is_blocked_by_them = serializers.SerializerMethodField()
    can_send_message = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'year_graduated', 'profile_picture', 'profile', 'is_blocked_by_me', 'is_blocked_by_them', 'can_send_message']

    def get_profile_picture(self, obj):
        if obj.profile_picture:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.profile_picture.url) if request else obj.profile_picture.url
        return None
    
    def get_is_blocked_by_me(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and hasattr(request.user, 'is_authenticated') and request.user.is_authenticated:
            return BlockedUser.objects.filter(user=request.user, blocked_user=obj).exists()
        return False
    
    def get_is_blocked_by_them(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and hasattr(request.user, 'is_authenticated') and request.user.is_authenticated:
            return BlockedUser.objects.filter(user=obj, blocked_user=request.user).exists()
        return False
    
    def get_can_send_message(self, obj):
        return not (self.get_is_blocked_by_me(obj) or self.get_is_blocked_by_them(obj))
