from rest_framework import serializers
from ..models import CustomUser
from .profile_model import ProfileModelSerializer


class UserSearchSerializer(serializers.ModelSerializer):
    profile = ProfileModelSerializer(read_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'profile_picture', 'profile']