from rest_framework import serializers
from ..models import PerceptionFurtherStudies


class PerceptionFurtherStudiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerceptionFurtherStudies
        exclude = ['user']