"""
Profile items serializers.
Contains serializers for Achievement, Education, Membership, Recognition, Training, 
Publication, Certificate, and CSEStatus models.
"""
from rest_framework import serializers
from ..models import (
    Achievement, Education, Membership, Recognition, Training, 
    Publication, Certificate, CSEStatus
)


class AchievementSerializer(serializers.ModelSerializer):
    """Serializer for Achievement model"""
    class Meta:
        model = Achievement
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']
    
    def to_internal_value(self, data):
        print(f"🔍 AchievementSerializer.to_internal_value() received data: {data}")
        print(f"🔍 AchievementSerializer.to_internal_value() data type: {type(data)}")
        
        # Log each field individually
        for field_name in ['title', 'type', 'url', 'attachment', 'organization', 'description', 'is_featured']:
            if field_name in data:
                field_value = data[field_name]
                print(f"🔍 Field '{field_name}': {field_value} (type: {type(field_value)})")
            else:
                print(f"❌ Field '{field_name}': MISSING from input data!")
        
        result = super().to_internal_value(data)
        print(f"✅ AchievementSerializer.to_internal_value() result: {result}")
        return result
        
    def create(self, validated_data):
        print(f"🔍 AchievementSerializer.create() validated_data: {validated_data}")
        achievement = super().create(validated_data)
        print(f"✅ AchievementSerializer.create() created: {achievement.__dict__}")
        return achievement


class EducationSerializer(serializers.ModelSerializer):
    """Serializer for Education model"""
    class Meta:
        model = Education
        fields = [
            'id', 'institution', 'degree_type', 'field_of_study', 
            'specialization', 'is_related_to_undergrad', 
            'reason_for_further_study', 'reason_other_specify',
            'start_date', 'end_date', 'is_current', 'description', 
            'user', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']


class MembershipSerializer(serializers.ModelSerializer):
    """Serializer for organization memberships"""
    is_current = serializers.ReadOnlyField()
    
    class Meta:
        model = Membership
        fields = [
            'id',
            'organization_name',
            'position',
            'membership_type',
            'date_joined',
            'date_ended',
            'description',
            'is_current',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate(self, data):
        """Validate that end date is after join date"""
        date_joined = data.get('date_joined')
        date_ended = data.get('date_ended')
        
        if date_joined and date_ended and date_ended < date_joined:
            raise serializers.ValidationError({
                'date_ended': 'End date must be after join date.'
            })
        
        return data


class RecognitionSerializer(serializers.ModelSerializer):
    """Serializer for recognitions and awards"""
    
    class Meta:
        model = Recognition
        fields = [
            'id',
            'title',
            'issuing_organization',
            'date_received',
            'description',
            'certificate_file',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class TrainingSerializer(serializers.ModelSerializer):
    """Serializer for trainings and seminars"""
    
    class Meta:
        model = Training
        fields = [
            'id',
            'title',
            'organization',
            'date_start',
            'date_end',
            'location',
            'certificate_file',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate(self, data):
        """Validate that end date is after start date"""
        date_start = data.get('date_start')
        date_end = data.get('date_end')
        
        if date_start and date_end and date_end < date_start:
            raise serializers.ValidationError({
                'date_end': 'End date must be after start date.'
            })
        
        return data


class PublicationSerializer(serializers.ModelSerializer):
    """Serializer for publications"""
    
    class Meta:
        model = Publication
        fields = [
            'id',
            'title',
            'publication_type',
            'authors',
            'date_published',
            'publisher',
            'url',
            'doi',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class CertificateSerializer(serializers.ModelSerializer):
    """Serializer for professional certificates"""
    is_active = serializers.ReadOnlyField()
    
    class Meta:
        model = Certificate
        fields = [
            'id',
            'certificate_type',
            'certificate_number',
            'date_issued',
            'expiry_date',
            'issuing_body',
            'certificate_file',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class CSEStatusSerializer(serializers.ModelSerializer):
    """Serializer for CSE (Current Student Employment) Status"""
    
    class Meta:
        model = CSEStatus
        fields = [
            'id',
            'status',
            'current_position',
            'current_company',
            'industry',
            'start_date',
            'end_date',
            'is_current',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate(self, data):
        """Validate that end date is after start date"""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError({
                'end_date': 'End date must be after start date.'
            })
        
        return data
