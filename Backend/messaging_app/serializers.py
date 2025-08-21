from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Message,
    GroupChat,
    MessageRequest,
    BlockedUser,
    Attachment,
    MessageReaction,  # Updated to use MessageReaction instead of Reaction
    LinkPreview,
    GroupMemberRequest,
    MessageRead  # Add MessageRead import
)
from auth_app.models import Profile  # Import Profile from auth_app

# ✅ Always fetch the correct user model dynamically
CustomUser = get_user_model()

# ✅ Profile Serializer (comes from auth_app.Profile)
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile  # Use auth_app.Profile, not messaging_app.UserProfile
        fields = ['status', 'bio', 'last_seen']

# ✅ Basic reusable User serializer
class UserSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'profile_picture', 'profile']

    def get_profile_picture(self, obj):
        if obj.profile_picture:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.profile_picture.url) if request else obj.profile_picture.url
        return None


# ✅ User Search Serializer (includes profile info)
class UserSearchSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()
    profile = UserProfileSerializer(read_only=True)
    is_blocked_by_me = serializers.SerializerMethodField()
    is_blocked_by_them = serializers.SerializerMethodField()
    can_send_message = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'year_graduated', 'profile_picture', 'profile', 'is_blocked_by_me', 'is_blocked_by_them', 'can_send_message']

    def get_profile_picture(self, obj):
        if obj.profile_picture:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.profile_picture.url) if request else obj.profile_picture.url
        return None
    
    def get_is_blocked_by_me(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and hasattr(request.user, 'is_authenticated') and request.user.is_authenticated:
            return BlockedUser.objects.filter(user=request.user, blocked_user=obj).exists()
        return False
    
    def get_is_blocked_by_them(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and hasattr(request.user, 'is_authenticated') and request.user.is_authenticated:
            return BlockedUser.objects.filter(user=obj, blocked_user=request.user).exists()
        return False
    
    def get_can_send_message(self, obj):
        return not (self.get_is_blocked_by_me(obj) or self.get_is_blocked_by_them(obj))


# ✅ Group Search Serializer
class GroupSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupChat
        fields = ['id', 'name', 'group_picture']

# ✅ Attachment Serializer (same logic as profile pictures)
class AttachmentSerializer(serializers.ModelSerializer):
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

# ✅ Message Reaction Serializer (Enhanced for Facebook-style reactions)
class MessageReactionSerializer(serializers.ModelSerializer):
    user = UserSearchSerializer(read_only=True)
    emoji = serializers.CharField(read_only=True)  # Auto-populated from reaction_type

    class Meta:
        model = MessageReaction
        fields = ['id', 'user', 'reaction_type', 'emoji', 'created_at']

# ✅ Legacy Reaction Serializer (for backward compatibility)
class ReactionSerializer(MessageReactionSerializer):
    """Legacy serializer - redirects to MessageReactionSerializer"""
    pass

# ✅ Link Preview Serializer
class LinkPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = LinkPreview
        fields = ['id', 'url', 'title', 'description', 'image_url', 'domain', 'created_at']

# ✅ Message Read Serializer
class MessageReadSerializer(serializers.ModelSerializer):
    user = UserSearchSerializer(read_only=True)
    
    class Meta:
        model = MessageRead
        fields = ['id', 'user', 'read_at']

# ✅ Message Serializer
class MessageSerializer(serializers.ModelSerializer):
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
        from django.db.models import Count
        
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
                'id': str(obj.reply_to.id),  # ✅ FIX: Convert UUID to string
                'content': obj.reply_to.content,
                'sender': {
                    'id': str(obj.reply_to.sender.id),  # ✅ FIX: Convert sender UUID to string
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

# ✅ Group Chat Serializer
class GroupChatSerializer(serializers.ModelSerializer):
    members = UserSearchSerializer(many=True, read_only=True)
    admins = UserSearchSerializer(many=True, read_only=True)
    group_picture = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = GroupChat
        fields = [
            'id',
            'name',
            'description',
            'group_picture',
            'members',
            'admins',
            'member_count',
            'created_at',
            'updated_at'
        ]
        
    def get_group_picture(self, obj):
        if obj.group_picture:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.group_picture.url) if request else obj.group_picture.url
        return None
        
    def get_member_count(self, obj):
        return obj.members.count()

# ✅ Message Request Serializer
class MessageRequestSerializer(serializers.ModelSerializer):
    sender = UserSearchSerializer(read_only=True)
    receiver = UserSearchSerializer(read_only=True)

    class Meta:
        model = MessageRequest
        fields = ['id', 'sender', 'receiver', 'content', 'timestamp', 'accepted']

# ✅ Blocked User Serializer
class BlockedUserSerializer(serializers.ModelSerializer):
    blocked_user = UserSearchSerializer()

    class Meta:
        model = BlockedUser
        fields = ['id', 'blocked_user', 'timestamp']

# ✅ Group Member Request Serializer
class GroupMemberRequestSerializer(serializers.ModelSerializer):
    requested_user = UserSearchSerializer(read_only=True)
    requester = UserSearchSerializer(read_only=True)
    reviewed_by = UserSearchSerializer(read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)

    class Meta:
        model = GroupMemberRequest
        fields = [
            'id',
            'group',
            'group_name',
            'requested_user',
            'requester',
            'status',
            'message',
            'admin_response',
            'reviewed_by',
            'created_at',
            'reviewed_at'
        ]



