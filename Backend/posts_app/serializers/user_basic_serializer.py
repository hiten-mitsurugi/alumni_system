from rest_framework import serializers
from auth_app.models import CustomUser


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user info for posts/comments"""
    profile_picture = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'full_name', 'email', 'profile_picture', 'user_type']
    
    def get_profile_picture(self, obj):
        if obj.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
        return None
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.email