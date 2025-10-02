from rest_framework import serializers
from ..models import MessageRead
from .user_search_serializer import UserSearchSerializer


class MessageReadSerializer(serializers.ModelSerializer):
    """Message Read Serializer"""
    user = UserSearchSerializer(read_only=True)
    
    class Meta:
        model = MessageRead
        fields = ['id', 'user', 'read_at']
