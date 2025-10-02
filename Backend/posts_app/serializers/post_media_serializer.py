from rest_framework import serializers
from ..models import PostMedia


class PostMediaSerializer(serializers.ModelSerializer):
    """Serializer for post media files"""
    file_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    
    class Meta:
        model = PostMedia
        fields = ['id', 'media_type', 'file_url', 'thumbnail_url', 'caption', 'order']
    
    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
        return None
    
    def get_thumbnail_url(self, obj):
        if obj.thumbnail:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.thumbnail.url)
        return None