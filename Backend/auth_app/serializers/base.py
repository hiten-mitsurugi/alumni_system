# Base serializer utilities and shared components
from rest_framework import serializers
import json


class AddressSerializer(serializers.Serializer):
    """Serializer for structured address data"""
    address_type = serializers.ChoiceField(choices=[('philippines', 'Philippines'), ('international', 'International')], required=False, default='philippines')
    # Philippines fields
    region_code = serializers.CharField(max_length=10, required=False, allow_blank=True)
    region_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    province_code = serializers.CharField(max_length=10, required=False, allow_blank=True)
    province_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    city_code = serializers.CharField(max_length=10, required=False, allow_blank=True)
    city_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    barangay = serializers.CharField(max_length=100, required=False, allow_blank=True)
    street_address = serializers.CharField(max_length=255, required=False, allow_blank=True)
    postal_code = serializers.CharField(max_length=10, required=False, allow_blank=True)
    # International fields
    country = serializers.CharField(max_length=100, required=False, allow_blank=True)
    full_address = serializers.CharField(required=False, allow_blank=True)


class JSONField(serializers.Field):
    """Custom JSON field for handling JSON data in serializers"""
    def to_internal_value(self, data):
        if not data:
            return {}
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            raise serializers.ValidationError("Invalid JSON format")