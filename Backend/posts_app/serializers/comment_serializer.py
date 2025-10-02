from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from ..models import Comment, Reaction
from .user_basic_serializer import UserBasicSerializer
from .reaction_serializer import ReactionSerializer


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