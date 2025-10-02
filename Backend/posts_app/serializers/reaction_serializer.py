from rest_framework import serializers
from ..models import Reaction
from .user_basic_serializer import UserBasicSerializer


class ReactionSerializer(serializers.ModelSerializer):
    """Enhanced reaction serializer with user info and emoji"""
    user = UserBasicSerializer(read_only=True)
    emoji = serializers.CharField(read_only=True)
    
    class Meta:
        model = Reaction
        fields = ['id', 'user', 'reaction_type', 'emoji', 'created_at']