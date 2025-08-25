from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import Post, Comment, Reaction, PostCategory, PostMedia, SavedPost, PostView, PostReport
from auth_app.models import CustomUser

class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user info for posts/comments"""
    profile_picture = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'full_name', 'email', 'profile_picture', 'user_type']
    
    def get_profile_picture(self, obj):
        if obj.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
        return None
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.email

class PostCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PostCategory
        fields = ['id', 'name', 'description']

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

class ReactionSerializer(serializers.ModelSerializer):
    """Enhanced reaction serializer with user info and emoji"""
    user = UserBasicSerializer(read_only=True)
    emoji = serializers.CharField(read_only=True)
    
    class Meta:
        model = Reaction
        fields = ['id', 'user', 'reaction_type', 'emoji', 'created_at']

class ReactionSummarySerializer(serializers.Serializer):
    """Summary of reactions for a post/comment"""
    total_count = serializers.IntegerField()
    user_reaction = serializers.CharField(allow_null=True)
    reaction_counts = serializers.DictField()
    recent_reactions = ReactionSerializer(many=True)

class CommentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating comments"""
    
    class Meta:
        model = Comment
        fields = ['content', 'parent']

class CommentSerializer(serializers.ModelSerializer):
    """Enhanced comment serializer with Facebook-like features"""
    user = UserBasicSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    reactions_summary = serializers.SerializerMethodField()
    is_edited = serializers.SerializerMethodField()
    time_since = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'user', 'post', 'content', 'parent', 'likes_count', 'replies_count',
            'created_at', 'updated_at', 'edited_at', 'is_edited', 'time_since',
            'replies', 'reactions_summary', 'can_edit', 'can_delete'
        ]
        extra_kwargs = {
            'post': {'required': False, 'read_only': True},
            'user': {'read_only': True}
        }
    
    def get_replies(self, obj):
        if obj.replies.exists():
            # Get first 3 replies ordered by creation date
            replies_queryset = obj.replies.all().order_by('created_at')[:3]
            return CommentSerializer(
                list(replies_queryset), 
                many=True, 
                context=self.context
            ).data
        return []
    
    def get_reactions_summary(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
            
        content_type = ContentType.objects.get_for_model(Comment)
        reactions = Reaction.objects.filter(
            content_type=content_type,
            object_id=obj.id
        ).select_related('user')
        
        total_count = reactions.count()
        user_reaction = None
        reaction_counts = {}
        
        if request.user.is_authenticated:
            user_reaction_obj = reactions.filter(user=request.user).first()
            if user_reaction_obj:
                user_reaction = user_reaction_obj.reaction_type
        
        # Count reactions by type
        for reaction in reactions:
            reaction_type = reaction.reaction_type
            if reaction_type not in reaction_counts:
                reaction_counts[reaction_type] = {
                    'count': 0,
                    'emoji': reaction.emoji
                }
            reaction_counts[reaction_type]['count'] += 1
        
        recent_reactions = ReactionSerializer(
            reactions.order_by('-created_at')[:5],
            many=True,
            context=self.context
        ).data
        
        return {
            'total_count': total_count,
            'user_reaction': user_reaction,
            'reaction_counts': reaction_counts,
            'recent_reactions': recent_reactions
        }
    
    def get_is_edited(self, obj):
        return obj.edited_at is not None
    
    def get_time_since(self, obj):
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff < timedelta(minutes=1):
            return "Just now"
        elif diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes}m"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f"{hours}h"
        elif diff < timedelta(days=7):
            days = diff.days
            return f"{days}d"
        else:
            return obj.created_at.strftime("%b %d")
    
    def get_can_edit(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.user == request.user
    
    def get_can_delete(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.user == request.user or request.user.user_type in [1, 2]

class PostSerializer(serializers.ModelSerializer):
    """Enhanced post serializer with Facebook-like features"""
    user = UserBasicSerializer(read_only=True)
    category = PostCategorySerializer(read_only=True)
    media_files = PostMediaSerializer(many=True, read_only=True)
    shared_post = serializers.SerializerMethodField()
    reactions_summary = serializers.SerializerMethodField()
    recent_comments = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    is_edited = serializers.SerializerMethodField()
    time_since = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()
    engagement_stats = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'user', 'title', 'content', 'content_category', 'category',
            'post_type', 'shared_post', 'shared_text', 'image', 'image_url',
            'media_files', 'likes_count', 'comments_count', 'shares_count',
            'is_approved', 'is_pinned', 'visibility', 'created_at', 'updated_at',
            'edited_at', 'is_edited', 'time_since', 'reactions_summary',
            'recent_comments', 'can_edit', 'can_delete', 'is_saved', 'engagement_stats'
        ]
    
    def get_shared_post(self, obj):
        if obj.shared_post:
            return PostSerializer(obj.shared_post, context=self.context).data
        return None
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
        return None
    
    def get_reactions_summary(self, obj):
        request = self.context.get('request')
        if not request:
            print(f"DEBUG: No request in context for post {obj.id}")
            return {
                'total_count': 0,
                'user_reaction': None,
                'reaction_counts': {},
                'recent_reactions': []
            }
            
        content_type = ContentType.objects.get_for_model(Post)
        reactions = Reaction.objects.filter(
            content_type=content_type,
            object_id=obj.id
        ).select_related('user')
        
        print(f"DEBUG: Found {reactions.count()} reactions for post {obj.id}")
        
        total_count = reactions.count()
        user_reaction = None
        reaction_counts = {}
        
        if request.user.is_authenticated:
            user_reaction_obj = reactions.filter(user=request.user).first()
            if user_reaction_obj:
                user_reaction = user_reaction_obj.reaction_type
                print(f"DEBUG: User {request.user.id} has reaction: {user_reaction}")
        
        # Count reactions by type
        for reaction in reactions:
            reaction_type = reaction.reaction_type
            if reaction_type not in reaction_counts:
                reaction_counts[reaction_type] = {
                    'count': 0,
                    'emoji': reaction.emoji
                }
            reaction_counts[reaction_type]['count'] += 1
        
        print(f"DEBUG: Reaction counts for post {obj.id}: {reaction_counts}")
        
        recent_reactions = ReactionSerializer(
            reactions.order_by('-created_at')[:5],
            many=True,
            context=self.context
        ).data
        
        result = {
            'total_count': total_count,
            'user_reaction': user_reaction,
            'reaction_counts': reaction_counts,
            'recent_reactions': recent_reactions
        }
        
        print(f"DEBUG: Final reactions_summary for post {obj.id}: {result}")
        return result
    
    def get_recent_comments(self, obj):
        # Get recent comments (first 3 top-level comments)
        recent_comments_queryset = obj.comments.filter(parent__isnull=True).order_by('-created_at')[:3]
        recent_comments = list(recent_comments_queryset)
        return CommentSerializer(recent_comments, many=True, context=self.context).data
    
    def get_is_edited(self, obj):
        return obj.edited_at is not None
    
    def get_time_since(self, obj):
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff < timedelta(minutes=1):
            return "Just now"
        elif diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes}m"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f"{hours}h"
        elif diff < timedelta(days=7):
            days = diff.days
            return f"{days}d"
        else:
            return obj.created_at.strftime("%b %d, %Y")
    
    def get_can_edit(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.user == request.user
    
    def get_can_delete(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.user == request.user or request.user.user_type in [1, 2]
    
    def get_is_saved(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return SavedPost.objects.filter(user=request.user, post=obj).exists()
    
    def get_engagement_stats(self, obj):
        return {
            'views_count': obj.views.count(),
            'engagement_rate': self._calculate_engagement_rate(obj),
        }
    
    def _calculate_engagement_rate(self, obj):
        """Calculate engagement rate as (reactions + comments + shares) / views"""
        views_count = obj.views.count()
        if views_count == 0:
            return 0
        
        total_engagement = obj.likes_count + obj.comments_count + obj.shares_count
        return round((total_engagement / views_count) * 100, 2)

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

class SavedPostSerializer(serializers.ModelSerializer):
    post = PostSerializer(read_only=True)
    
    class Meta:
        model = SavedPost
        fields = ['id', 'post', 'created_at']

class PostReportSerializer(serializers.ModelSerializer):
    reporter = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = PostReport
        fields = ['id', 'reason', 'description', 'reporter', 'created_at', 'is_resolved']