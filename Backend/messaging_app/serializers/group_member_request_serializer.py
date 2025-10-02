from rest_framework import serializers
from ..models import GroupMemberRequest
from .user_search_serializer import UserSearchSerializer


class GroupMemberRequestSerializer(serializers.ModelSerializer):
    """Group Member Request Serializer"""
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
