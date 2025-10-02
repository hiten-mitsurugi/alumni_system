from rest_framework import serializers
from django.db.models import Count
from ..models import Message, MessageReaction, MessageRead
from .user_search_serializer import UserSearchSerializer
from .attachment_serializer import AttachmentSerializer
from .message_reaction_serializer import MessageReactionSerializer
from .link_preview_serializer import LinkPreviewSerializer


class MessageSerializer(serializers.ModelSerializer):
    """Message Serializer"""
    sender = UserSearchSerializer(read_only=True)
    receiver = UserSearchSerializer(read_only=True)
    reply_to = serializers.SerializerMethodField()
    forwarded_from = serializers.SerializerMethodField()
    attachments = AttachmentSerializer(many=True, read_only=True)
    reactions = MessageReactionSerializer(many=True, read_only=True)
    reaction_stats = serializers.SerializerMethodField()  # Add reaction statistics
    link_previews = LinkPreviewSerializer(many=True, read_only=True)
    read_by = serializers.SerializerMethodField()  # Add seen indicator data

    class Meta:
        model = Message
        fields = [
            'id',
            'sender',
            'receiver',
            'group',
            'content',
            'timestamp',
            'edited_at',  # Add edited_at field
            'is_read',
            'reply_to',
            'forwarded_from',
            'is_forwarded',
            'attachments',
            'is_pinned',
            'reactions',
            'reaction_stats',  # Add reaction statistics
            'link_previews',
            'read_by'  # Add seen indicator data
        ]

    def get_reaction_stats(self, obj):
        """Get reaction statistics for this message"""
        # Get reaction counts grouped by type
        reaction_counts = MessageReaction.objects.filter(
            message=obj
        ).values('reaction_type', 'emoji').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Get reactions by type with user info
        reactions_by_type = {}
        for reaction_type_info in MessageReaction.REACTION_CHOICES:
            reaction_type = reaction_type_info[0]
            reactions = MessageReaction.objects.filter(
                message=obj,
                reaction_type=reaction_type
            ).select_related('user')
            
            if reactions.exists():
                reactions_by_type[reaction_type] = {
                    'emoji': reaction_type_info[1],
                    'count': reactions.count(),
                    'users': [
                        {
                            'id': r.user.id,
                            'name': f"{r.user.first_name} {r.user.last_name}".strip() or r.user.username
                        }
                        for r in reactions
                    ]
                }
        
        return {
            'total_reactions': MessageReaction.objects.filter(message=obj).count(),
            'reaction_counts': list(reaction_counts),
            'reactions_by_type': reactions_by_type
        }

    def get_read_by(self, obj):
        """Get users who have read this message (for seen indicators)"""
        # For private messages, we use the simple is_read field
        if obj.receiver:
            if obj.is_read:
                return [{
                    'id': obj.receiver.id,
                    'first_name': obj.receiver.first_name,
                    'last_name': obj.receiver.last_name,
                    'profile_picture': self.get_profile_picture_url(obj.receiver),
                    'read_at': obj.timestamp.isoformat()  # Use message timestamp as fallback
                }]
            return []
        
        # For group messages, use MessageRead records
        elif obj.group:
            read_records = MessageRead.objects.filter(message=obj).select_related('user')
            return [{
                'id': record.user.id,
                'first_name': record.user.first_name,
                'last_name': record.user.last_name,
                'profile_picture': self.get_profile_picture_url(record.user),
                'read_at': record.read_at.isoformat()
            } for record in read_records]
        
        return []

    def get_reply_to(self, obj):
        if obj.reply_to:
            return {
                'id': str(obj.reply_to.id),  # Convert UUID to string
                'content': obj.reply_to.content,
                'sender': {
                    'id': str(obj.reply_to.sender.id),  # Convert sender UUID to string
                    'first_name': obj.reply_to.sender.first_name,
                    'last_name': obj.reply_to.sender.last_name,
                    'profile_picture': self.get_profile_picture_url(obj.reply_to.sender)
                }
            }
        return None

    def get_forwarded_from(self, obj):
        if obj.forwarded_from:
            return {
                'id': str(obj.forwarded_from.id),
                'content': obj.forwarded_from.content,
                'sender': {
                    'id': str(obj.forwarded_from.sender.id),
                    'first_name': obj.forwarded_from.sender.first_name,
                    'last_name': obj.forwarded_from.sender.last_name,
                    'profile_picture': self.get_profile_picture_url(obj.forwarded_from.sender)
                },
                'timestamp': obj.forwarded_from.timestamp.isoformat(),
                'was_group_message': bool(obj.forwarded_from.group),
                'original_group_name': obj.forwarded_from.group.name if obj.forwarded_from.group else None
            }
        return None

    def get_profile_picture_url(self, user):
        if user.profile_picture:
            request = self.context.get('request')
            return request.build_absolute_uri(user.profile_picture.url) if request else user.profile_picture.url
        return None

    def to_representation(self, instance):
        # Pass request context to nested serializers
        data = super().to_representation(instance)
        if self.context.get('request'):
            data['attachments'] = AttachmentSerializer(
                instance.attachments.all(), 
                many=True, 
                context=self.context
            ).data
        return data
