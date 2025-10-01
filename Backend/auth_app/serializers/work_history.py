from rest_framework import serializers
from ..models import WorkHistory
from .skill import SkillSerializer


class WorkHistorySerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, required=False)
    
    class Meta:
        model = WorkHistory
        exclude = ['user']