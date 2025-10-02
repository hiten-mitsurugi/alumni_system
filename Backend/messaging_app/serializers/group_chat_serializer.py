from rest_framework import serializers
from ..models import GroupChat
from .user_search_serializer import UserSearchSerializer


class GroupChatSerializer(serializers.ModelSerializer):
    """Group Chat Serializer"""
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
