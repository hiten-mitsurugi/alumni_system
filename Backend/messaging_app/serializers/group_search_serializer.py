from rest_framework import serializers
from ..models import GroupChat


class GroupSearchSerializer(serializers.ModelSerializer):
    """Group Search Serializer"""
    class Meta:
        model = GroupChat
        fields = ['id', 'name', 'group_picture']
