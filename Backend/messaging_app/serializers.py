from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Message,
    GroupChat,
    MessageRequest,
    BlockedUser,
    MutedConversation,
    Attachment,
    Reaction
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

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'year_graduated', 'profile_picture', 'profile']

    def get_profile_picture(self, obj):
        if obj.profile_picture:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.profile_picture.url) if request else obj.profile_picture.url
        return None


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
        fields = ['id', 'file', 'file_type']

    def get_file(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            else:
                return obj.file.url
        return None

# ✅ Reaction Serializer
class ReactionSerializer(serializers.ModelSerializer):
    user = UserSearchSerializer(read_only=True)

    class Meta:
        model = Reaction
        fields = ['id', 'user', 'emoji']

# ✅ Message Serializer
class MessageSerializer(serializers.ModelSerializer):
    sender = UserSearchSerializer(read_only=True)
    receiver = UserSearchSerializer(read_only=True)
    reply_to = serializers.SerializerMethodField()
    attachments = AttachmentSerializer(many=True, read_only=True)
    reactions = ReactionSerializer(many=True, read_only=True)

    class Meta:
        model = Message
        fields = [
            'id',
            'sender',
            'receiver',
            'group',
            'content',
            'timestamp',
            'is_read',
            'reply_to',
            'attachments',
            'is_pinned',
            'reactions'
        ]

    def get_reply_to(self, obj):
        if obj.reply_to:
            return {
                'id': str(obj.reply_to.id),  # ✅ FIX: Convert UUID to string
                'content': obj.reply_to.content,
                'sender': {
                    'id': obj.reply_to.sender.id,
                    'first_name': obj.reply_to.sender.first_name,
                    'last_name': obj.reply_to.sender.last_name,
                    'profile_picture': self.get_profile_picture_url(obj.reply_to.sender)
                }
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

    class Meta:
        model = GroupChat
        fields = [
            'id',
            'name',
            'group_picture',
            'members',
            'admins',
            'created_at'
        ]

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

# ✅ Muted Conversation Serializer
class MutedConversationSerializer(serializers.ModelSerializer):
    receiver = UserSearchSerializer(read_only=True)
    group = GroupChatSerializer(read_only=True)

    class Meta:
        model = MutedConversation
        fields = ['id', 'receiver', 'group', 'muted_until']
