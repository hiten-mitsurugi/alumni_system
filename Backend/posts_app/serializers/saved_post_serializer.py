from rest_framework import serializers
from ..models import SavedPost


class SavedPostSerializer(serializers.ModelSerializer):
    post = serializers.SerializerMethodField()
    
    class Meta:
        model = SavedPost
        fields = ['id', 'post', 'created_at']
    
    def get_post(self, obj):
        # Import here to avoid circular import
        from .post_serializer import PostSerializer
        return PostSerializer(obj.post, context=self.context).data