from rest_framework import serializers
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from ..models import CustomUser


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    government_id = serializers.FileField(allow_null=True, required=False)
    profile_picture = serializers.ImageField(allow_null=True, required=False)
    user_type = serializers.ChoiceField(choices=CustomUser.USER_TYPE_CHOICES)
    civil_status = serializers.ChoiceField(choices=CustomUser.CIVIL_STATUS_CHOICES, required=False)

    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'middle_name', 'last_name', 'email', 'password',
            'government_id', 'program', 'present_address', 'permanent_address',
            'profile_picture', 'contact_number', 'sex', 'user_type', 'is_approved',
            'birth_date', 'year_graduated', 'employment_status', 'civil_status'
        ]

    def validate_email(self, value):
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Invalid email address.")
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, data):
        request = self.context.get('request')
        if data['user_type'] == 1:
            if not request or not request.user.is_authenticated or request.user.user_type != 1:
                raise serializers.ValidationError("Only Super Admins can create Super Admin users.")
        if data['user_type'] == 3 and not data.get('is_approved', False):
            data['is_approved'] = False
        return data

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            middle_name=validated_data.get('middle_name', ''),
            last_name=validated_data['last_name'],
            government_id=validated_data.get('government_id'),
            program=validated_data.get('program', ''),
            present_address=validated_data['present_address'],
            permanent_address=validated_data['permanent_address'],
            profile_picture=validated_data.get('profile_picture'),
            contact_number=validated_data.get('contact_number', ''),
            sex=validated_data.get('sex', ''),
            civil_status=validated_data.get('civil_status', ''),
            user_type=validated_data['user_type'],
            is_approved=validated_data.get('is_approved', False),
            birth_date=validated_data.get('birth_date'),
            year_graduated=validated_data.get('year_graduated'),
            employment_status=validated_data.get('employment_status')
        )
        return user