"""
Base serializers for common fields and utilities.
Contains JSONField, AddressSerializer, and AlumniDirectorySerializer.
"""
from rest_framework import serializers
import json
from ..models import Address, AlumniDirectory


class JSONField(serializers.Field):
    """Custom JSON field serializer"""
    def to_internal_value(self, data):
        if not data:
            return {}
        
        # If data is already a dict/object, return it as-is
        if isinstance(data, dict):
            return data
            
        # If data is a string, try to parse it as JSON
        if isinstance(data, str):
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                raise serializers.ValidationError("Invalid JSON format")
        
        # For other types, try to convert to dict
        return dict(data) if data else {}


class AddressSerializer(serializers.ModelSerializer):
    """Serializer for the Address model"""
    class Meta:
        model = Address
        exclude = ['user', 'id', 'created_at', 'updated_at', 'normalized_text']


class AlumniDirectorySerializer(serializers.ModelSerializer):
    """Serializer for AlumniDirectory model"""
    class Meta:
        model = AlumniDirectory
        fields = ['id', 'first_name', 'middle_name', 'last_name', 'birth_date', 'program', 'year_graduated', 'sex']
