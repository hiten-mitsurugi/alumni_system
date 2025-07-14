from rest_framework import serializers
from .models import Message, GroupChat, Reaction, Attachment, MessageRequest, BlockedUser, MutedConversation, UserProfile
from django.contrib.auth import get_user_model

User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['status', 'last_seen', 'profile_picture']

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']

class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['id', 'file', 'file_type']

class ReactionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Reaction
        fields = ['id', 'user', 'reaction_type']

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True, allow_null=True)
    group = serializers.PrimaryKeyRelatedField(queryset=GroupChat.objects.all(), allow_null=True)
    reactions = ReactionSerializer(many=True, read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    reply_to = serializers.PrimaryKeyRelatedField(queryset=Message.objects.all(), allow_null=True)
    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'group', 'content', 'timestamp', 'is_read', 'is_pinned', 'reactions', 'attachments', 'reply_to']

class GroupChatSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)
    admins = UserSerializer(many=True, read_only=True)
    class Meta:
        model = GroupChat
        fields = ['id', 'name', 'members', 'admins', 'created_at', 'group_picture']

class MessageRequestSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    class Meta:
        model = MessageRequest
        fields = ['id', 'sender', 'receiver', 'timestamp', 'accepted']

class BlockedUserSerializer(serializers.ModelSerializer):
    blocked_user = UserSerializer(read_only=True)
    class Meta:
        model = BlockedUser
        fields = ['id', 'blocked_user', 'timestamp']

class MutedConversationSerializer(serializers.ModelSerializer):
    receiver = UserSerializer(read_only=True)
    group = GroupChatSerializer(read_only=True)
    class Meta:
        model = MutedConversation
        fields = ['id', 'user', 'group', 'receiver', 'muted_until']