from rest_framework import serializers
from ..models import Comment


class CommentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating comments"""
    
    class Meta:
        model = Comment
        fields = ['content', 'parent']