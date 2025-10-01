from rest_framework import serializers
from ..models import Profile


class ProfileModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ['user']