from rest_framework import serializers
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, Skill, WorkHistory, AlumniDirectory
import re

class AlumniDirectoryCheckSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True)
    middle_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    last_name = serializers.CharField(required=True)
    school_id = serializers.CharField(required=True)
    program = serializers.CharField(required=True)
    birth_date = serializers.DateField(required=True)
    year_graduated = serializers.IntegerField(required=True)
    gender = serializers.ChoiceField(choices=CustomUser.GENDER_CHOICES, required=True)

    def validate_school_id(self, value):
        if not re.match(r'^\d{3}-\d{5}$', value):
            raise serializers.ValidationError("School ID must be in the format 123-45678.")
        return value

    def validate_gender(self, value):
        value_lower = value.lower()
        valid_choices = [choice[0] for choice in CustomUser.GENDER_CHOICES]
        if value_lower not in valid_choices:
            raise serializers.ValidationError(f'"{value}" is not a valid choice.')
        return value_lower

    def validate(self, data):
        try:
            query = {
                'school_id': data['school_id'],
                'first_name__iexact': data['first_name'],
                'last_name__iexact': data['last_name'],
                'birth_date': data['birth_date'],
                'program__iexact': data['program'],
                'year_graduated': data['year_graduated'],
                'gender': data['gender']
            }
            if data.get('middle_name'):
                query['middle_name__iexact'] = data['middle_name']
            else:
                query['middle_name__isnull'] = True
            alumni = AlumniDirectory.objects.get(**query)
            return {'exists': True, 'alumni': alumni}
        except AlumniDirectory.DoesNotExist:
            raise serializers.ValidationError("Not an existing alumni. Please contact the Alumni Relations Office.")

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    school_id = serializers.CharField(required=True)
    program = serializers.CharField(required=True)
    birth_date = serializers.DateField(required=True)
    year_graduated = serializers.IntegerField(required=True)
    gender = serializers.ChoiceField(choices=CustomUser.GENDER_CHOICES, required=True)
    civil_status = serializers.ChoiceField(choices=CustomUser.CIVIL_STATUS_CHOICES, required=True)
    email = serializers.CharField(required=True)
    address = serializers.CharField(required=True)
    contact_number = serializers.CharField(required=True)
    employment_status = serializers.ChoiceField(
        choices=['employed_locally', 'employed_internationally', 'self_employed', 'unemployed'],
        required=True
    )
    government_id = serializers.FileField(required=True, allow_null=False)
    profile_picture = serializers.ImageField(required=True, allow_null=False)
    alumni_exists = serializers.BooleanField(write_only=True, default=False)

    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'middle_name', 'last_name', 'email', 'password', 'confirm_password',
            'school_id', 'government_id', 'program', 'address', 'profile_picture',
            'contact_number', 'gender', 'birth_date', 'year_graduated', 'employment_status',
            'civil_status', 'alumni_exists'
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
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        validated_data.pop('alumni_exists')
        if not validated_data.get('middle_name'):
            validated_data['middle_name'] = ''
        user = CustomUser.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            middle_name=validated_data['middle_name'],
            last_name=validated_data['last_name'],
            school_id=validated_data['school_id'],
            government_id=validated_data['government_id'],
            program=validated_data['program'],
            address=validated_data['address'],
            profile_picture=validated_data['profile_picture'],
            contact_number=validated_data['contact_number'],
            gender=validated_data['gender'],
            civil_status=validated_data['civil_status'],
            birth_date=validated_data['birth_date'],
            year_graduated=validated_data['year_graduated'],
            employment_status=validated_data['employment_status'],
            user_type=3,
            is_approved=False,
        )
        return user

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    government_id = serializers.FileField(required=False, allow_null=True)
    profile_picture = serializers.ImageField(required=False, allow_null=True)
    user_type = serializers.ChoiceField(choices=CustomUser.USER_TYPE_CHOICES)
    is_approved = serializers.BooleanField(default=False)
    civil_status = serializers.ChoiceField(choices=CustomUser.CIVIL_STATUS_CHOICES, required=False)

    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'middle_name', 'last_name', 'email', 'password',
            'school_id', 'government_id', 'program', 'address', 'profile_picture',
            'contact_number', 'gender', 'user_type', 'is_approved',
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
            school_id=validated_data.get('school_id', ''),
            government_id=validated_data.get('government_id'),
            program=validated_data.get('program', ''),
            address=validated_data.get('address', ''),
            profile_picture=validated_data.get('profile_picture'),
            contact_number=validated_data.get('contact_number', ''),
            gender=validated_data.get('gender', ''),
            civil_status=validated_data.get('civil_status', ''),
            user_type=validated_data['user_type'],
            is_approved=validated_data.get('is_approved', False),
            birth_date=validated_data.get('birth_date'),
            year_graduated=validated_data.get('year_graduated'),
            employment_status=validated_data.get('employment_status'),
        )
        return user

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name']

class WorkHistorySerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True)

    class Meta:
        model = WorkHistory
        fields = [
            'id', 'user', 'company_name', 'company_address', 'position',
            'start_date', 'end_date', 'skills'
        ]

    def create(self, validated_data):
        skills_data = validated_data.pop('skills', [])
        work_history = WorkHistory.objects.create(**validated_data)
        for skill_data in skills_data:
            skill, _ = Skill.objects.get_or_create(**skill_data)
            work_history.skills.add(skill)
        return work_history

    def update(self, instance, validated_data):
        skills_data = validated_data.pop('skills', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if skills_data is not None:
            instance.skills.clear()
            for skill_data in skills_data:
                skill, _ = Skill.objects.get_or_create(**skill_data)
                instance.skills.add(skill)
        return instance

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [field.name for field in CustomUser._meta.fields if field.name != 'password']

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'school_id', 'first_name', 'middle_name',
            'last_name', 'program', 'user_type', 'is_approved',
            'birth_date', 'year_graduated', 'employment_status', 'civil_status'
        ]

class AlumniDirectorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AlumniDirectory
        fields = ['first_name', 'middle_name', 'last_name', 'birth_date', 'school_id', 'program', 'year_graduated', 'gender']

