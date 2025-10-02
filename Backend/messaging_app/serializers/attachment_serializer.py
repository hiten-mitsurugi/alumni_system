from rest_framework import serializers
from ..models import Attachment


class AttachmentSerializer(serializers.ModelSerializer):
    """Attachment Serializer (same logic as profile pictures)"""
    file = serializers.SerializerMethodField()

    class Meta:
        model = Attachment
        fields = ['id', 'file', 'file_name', 'file_type', 'file_size', 'uploaded_at']

    def get_file(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            else:
                return obj.file.url
        return None
