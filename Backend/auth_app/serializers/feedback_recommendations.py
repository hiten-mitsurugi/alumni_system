from rest_framework import serializers
from ..models import FeedbackRecommendations


class FeedbackRecommendationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackRecommendations
        exclude = ['user']