from rest_framework import serializers
from ..models import Education


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']