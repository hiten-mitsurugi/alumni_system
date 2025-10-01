from rest_framework import serializers
from ..models import AlumniDirectory


class AlumniDirectorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AlumniDirectory
        fields = ['id', 'first_name', 'middle_name', 'last_name', 'birth_date', 'program', 'year_graduated', 'sex']