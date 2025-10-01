from rest_framework import serializers
from ..models import Achievement


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']