from rest_framework import serializers
from .models import Post, Comment, Reaction, PostCategory
from auth_app.models import CustomUser

class PostCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PostCategory
        fields = ['id', 'name', 'description']

class ReactionSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='email', queryset=CustomUser.objects.all())
    content_type = serializers.CharField(source='content_type.model', read_only=True)
    object_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Reaction
        fields = ['id', 'user', 'reaction_type', 'content_type', 'object_id', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='email', queryset=CustomUser.objects.all())
    replies = serializers.SerializerMethodField()
    reactions = ReactionSerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'parent', 'created_at', 'replies', 'reactions']

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []

class PostSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='email', queryset=CustomUser.objects.all())
    category = PostCategorySerializer()
    comments = CommentSerializer(many=True, read_only=True)
    reactions = ReactionSerializer(many=True, read_only=True)
    image = serializers.ImageField(required=False)

    class Meta:
        model = Post
        fields = ['id', 'user', 'title', 'content', 'content_category', 'category', 'image', 'is_approved', 'created_at', 'updated_at', 'comments', 'reactions']

    def create(self, validated_data):
        category_data = validated_data.pop('category')
        category, _ = PostCategory.objects.get_or_create(**category_data)
        post = Post.objects.create(category=category, **validated_data)
        return post