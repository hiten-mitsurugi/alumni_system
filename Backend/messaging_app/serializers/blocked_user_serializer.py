from rest_framework import serializers
from ..models import BlockedUser
from .user_search_serializer import UserSearchSerializer


class BlockedUserSerializer(serializers.ModelSerializer):
    """Blocked User Serializer"""
    blocked_user = UserSearchSerializer()

    class Meta:
        model = BlockedUser
        fields = ['id', 'blocked_user', 'timestamp']
