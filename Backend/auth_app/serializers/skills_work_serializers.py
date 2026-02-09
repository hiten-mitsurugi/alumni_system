"""
Skills and work history serializers.
Contains serializers for Skill, UserSkill, and WorkHistory models.
"""
from rest_framework import serializers
from ..models import Skill, UserSkill, WorkHistory


class SkillSerializer(serializers.ModelSerializer):
    """Serializer for Skill model"""
    class Meta:
        model = Skill
        fields = ['id', 'name']


class UserSkillSerializer(serializers.ModelSerializer):
    """Serializer for UserSkill model"""
    class Meta:
        model = UserSkill
        exclude = ['user']


class WorkHistorySerializer(serializers.ModelSerializer):
    """Serializer for WorkHistory model"""
    class Meta:
        model = WorkHistory
        fields = [
            'id', 'job_type', 'employment_status', 'classification',
            'occupation', 'employing_agency', 'how_got_job', 'monthly_income',
            'is_breadwinner', 'length_of_service', 'college_education_relevant',
            'start_date', 'end_date', 'description'
        ]
