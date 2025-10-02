from rest_framework import serializers
from ..models import LinkPreview


class LinkPreviewSerializer(serializers.ModelSerializer):
    """Link Preview Serializer"""
    class Meta:
        model = LinkPreview
        fields = ['id', 'url', 'title', 'description', 'image_url', 'domain', 'created_at']
