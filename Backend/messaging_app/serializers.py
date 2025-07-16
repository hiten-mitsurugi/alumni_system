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

# ✅ Basic reusable User serializer
class UserSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'profile_picture']

    def get_profile_picture(self, obj):
        if obj.profile_picture:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.profile_picture.url) if request else obj.profile_picture.url
        return None


# ✅ Profile Serializer (comes from auth_app.Profile)
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile  # Use auth_app.Profile, not messaging_app.UserProfile
        fields = ['profile_picture', 'status', 'bio', 'last_seen']

# ✅ User Search Serializer (includes profile info)
class UserSearchSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'year_graduated', 'profile_picture']

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

# ✅ Attachment Serializer
class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['id', 'file']  # Only include file unless you need file_type

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
    attachments = AttachmentSerializer(many=True, read_only=True)
    reactions = ReactionSerializer(many=True, read_only=True)
    reply_to = serializers.UUIDField(read_only=True)

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
            'attachments',
            'is_pinned',
            'reactions',
            'reply_to'
        ]

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
        fields = ['id', 'sender', 'receiver', 'timestamp', 'accepted']

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
