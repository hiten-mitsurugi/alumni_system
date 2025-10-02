from rest_framework import serializers
from django.contrib.auth import get_user_model
from .user_profile_serializer import UserProfileSerializer


CustomUser = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Basic reusable User serializer"""
    profile_picture = serializers.SerializerMethodField()
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'profile_picture', 'profile']

    def get_profile_picture(self, obj):
        if obj.profile_picture:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.profile_picture.url) if request else obj.profile_picture.url
        return None
