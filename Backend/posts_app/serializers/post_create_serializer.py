from rest_framework import serializers
from ..models import Post, PostMedia


class PostCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating posts"""
    media_files = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        write_only=True
    )
    
    class Meta:
        model = Post
        fields = [
            'title', 'content', 'content_category', 'post_type', 
            'shared_post', 'shared_text', 'visibility', 'image', 'media_files'
        ]
    
    def create(self, validated_data):
        media_files = validated_data.pop('media_files', [])
        user = self.context['request'].user
        
        # Auto-approve admin posts
        is_approved = user.user_type in [1, 2]
        
        post = Post.objects.create(
            user=user,
            is_approved=is_approved,
            **validated_data
        )
        
        # Handle media files
        for index, media_file in enumerate(media_files):
            # Determine media type based on file extension
            file_name = media_file.name.lower()
            if file_name.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                media_type = 'image'
            elif file_name.endswith(('.mp4', '.avi', '.mov', '.webm')):
                media_type = 'video'
            else:
                media_type = 'document'
            
            PostMedia.objects.create(
                post=post,
                media_type=media_type,
                file=media_file,
                order=index
            )
        
        return post