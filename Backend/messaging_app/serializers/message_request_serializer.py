from rest_framework import serializers
from ..models import MessageRequest
from .user_search_serializer import UserSearchSerializer


class MessageRequestSerializer(serializers.ModelSerializer):
    """Message Request Serializer"""
    sender = UserSearchSerializer(read_only=True)
    receiver = UserSearchSerializer(read_only=True)

    class Meta:
        model = MessageRequest
        fields = ['id', 'sender', 'receiver', 'content', 'timestamp', 'accepted']
