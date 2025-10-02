from rest_framework import serializers
from ..models import PostReport
from .user_basic_serializer import UserBasicSerializer


class PostReportSerializer(serializers.ModelSerializer):
    reporter = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = PostReport
        fields = ['id', 'reason', 'description', 'reporter', 'created_at', 'is_resolved']