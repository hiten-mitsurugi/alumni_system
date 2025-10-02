from rest_framework import serializers
from .reaction_serializer import ReactionSerializer


class ReactionSummarySerializer(serializers.Serializer):
    """Summary of reactions for a post/comment"""
    total_count = serializers.IntegerField()
    user_reaction = serializers.CharField(allow_null=True)
    reaction_counts = serializers.DictField()
    recent_reactions = ReactionSerializer(many=True)