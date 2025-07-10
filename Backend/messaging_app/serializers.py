from rest_framework import serializers
from .models import Message, GroupChat, Reaction, Attachment
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

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

    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'group', 'content', 'timestamp', 'is_read', 'reactions', 'attachments']

class GroupChatSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)
    admins = UserSerializer(many=True, read_only=True)

    class Meta:
        model = GroupChat
        fields = ['id', 'name', 'members', 'admins', 'created_at']