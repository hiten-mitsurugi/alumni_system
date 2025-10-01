from rest_framework import serializers
from ..models import CurriculumRelevance


class CurriculumRelevanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurriculumRelevance
        exclude = ['user']