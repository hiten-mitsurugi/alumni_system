from rest_framework import serializers
from ..models import SkillsRelevance


class SkillsRelevanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillsRelevance
        exclude = ['user']