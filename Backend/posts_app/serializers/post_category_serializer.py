from rest_framework import serializers
from ..models import PostCategory


class PostCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PostCategory
        fields = ['id', 'name', 'description']