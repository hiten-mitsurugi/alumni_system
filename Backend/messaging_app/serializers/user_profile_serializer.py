from rest_framework import serializers
from auth_app.models import Profile


class UserProfileSerializer(serializers.ModelSerializer):
    """Profile Serializer (comes from auth_app.Profile)"""
    class Meta:
        model = Profile  # Use auth_app.Profile, not messaging_app.UserProfile
        fields = ['status', 'bio', 'last_seen']
