"""
Survey-related serializers for legacy questionnaire data.
Contains serializers for SkillsRelevance, CurriculumRelevance, PerceptionFurtherStudies, and FeedbackRecommendations.
"""
from rest_framework import serializers
from ..models import (
    SkillsRelevance, CurriculumRelevance, 
    PerceptionFurtherStudies, FeedbackRecommendations
)


class SkillsRelevanceSerializer(serializers.ModelSerializer):
    """Serializer for SkillsRelevance model"""
    class Meta:
        model = SkillsRelevance
        exclude = ['user']


class CurriculumRelevanceSerializer(serializers.ModelSerializer):
    """Serializer for CurriculumRelevance model"""
    class Meta:
        model = CurriculumRelevance
        exclude = ['user']


class PerceptionFurtherStudiesSerializer(serializers.ModelSerializer):
    """Serializer for PerceptionFurtherStudies model"""
    class Meta:
        model = PerceptionFurtherStudies
        exclude = ['user']


class FeedbackRecommendationsSerializer(serializers.ModelSerializer):
    """Serializer for FeedbackRecommendations model"""
    class Meta:
        model = FeedbackRecommendations
        exclude = ['user']
