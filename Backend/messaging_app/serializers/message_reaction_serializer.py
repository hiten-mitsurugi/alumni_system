from rest_framework import serializers
from ..models import MessageReaction
from .user_search_serializer import UserSearchSerializer


class MessageReactionSerializer(serializers.ModelSerializer):
    """Message Reaction Serializer (Enhanced for Facebook-style reactions)"""
    user = UserSearchSerializer(read_only=True)
    emoji = serializers.CharField(read_only=True)  # Auto-populated from reaction_type

    class Meta:
        model = MessageReaction
        fields = ['id', 'user', 'reaction_type', 'emoji', 'created_at']
