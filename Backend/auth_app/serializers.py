from rest_framework import serializers
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
import re
import json

from .models import (
    CustomUser, Skill, WorkHistory, AlumniDirectory, SkillsRelevance,
    CurriculumRelevance, PerceptionFurtherStudies, FeedbackRecommendations, Profile
)

class JSONField(serializers.Field):
    def to_internal_value(self, data):
        if not data:
            return {}
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            raise serializers.ValidationError("Invalid JSON format")

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
        valid_choices = [choice[0] for choice in CustomUser.GENDER_CHOICES]
        if value not in valid_choices:
            raise serializers.ValidationError(f'"{value}" is not a valid choice.')
        return value

    def validate(self, data):
        from .models import AlumniDirectory  # Move import to top
        
        try:
            query = {
                'school_id': data['school_id'],
                'first_name__iexact': data['first_name'],
                'last_name__iexact': data['last_name'],
                'birth_date': data['birth_date'],
                'program__iexact': data['program'],
                'year_graduated': data['year_graduated'],
                'gender__iexact': data['gender']  # Changed to case insensitive
            }
            
            if data.get('middle_name') and data['middle_name'].strip():
                query['middle_name__iexact'] = data['middle_name'].strip()
            else:
                # Check for both null and empty string
                query_null = query.copy()
                query_null['middle_name__isnull'] = True
                query_empty = query.copy()
                query_empty['middle_name__exact'] = ''
                
                # Try both queries
                try:
                    alumni = AlumniDirectory.objects.get(**query_null)
                    return {'exists': True, 'alumni': alumni}
                except AlumniDirectory.DoesNotExist:
                    try:
                        alumni = AlumniDirectory.objects.get(**query_empty)
                        return {'exists': True, 'alumni': alumni}
                    except AlumniDirectory.DoesNotExist:
                        pass
                raise AlumniDirectory.DoesNotExist("No match found for empty/null middle name")
            
            alumni = AlumniDirectory.objects.get(**query)
            return {'exists': True, 'alumni': alumni}
        except AlumniDirectory.DoesNotExist:
            raise serializers.ValidationError("Not an existing alumni. Please contact the Alumni Relations Office.")

class AlumniDirectorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AlumniDirectory
        fields = ['first_name', 'middle_name', 'last_name', 'birth_date', 'school_id', 'program', 'year_graduated', 'gender']

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name']

class WorkHistorySerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, required=False)
    class Meta:
        model = WorkHistory
        exclude = ['user']

class SkillsRelevanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillsRelevance
        exclude = ['user']

class CurriculumRelevanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurriculumRelevance
        exclude = ['user']

class PerceptionFurtherStudiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerceptionFurtherStudies
        exclude = ['user']

class FeedbackRecommendationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackRecommendations
        exclude = ['user']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    gender = serializers.ChoiceField(choices=CustomUser.GENDER_CHOICES, required=True)
    civil_status = serializers.ChoiceField(choices=CustomUser.CIVIL_STATUS_CHOICES, required=True)
    employment_status = serializers.ChoiceField(choices=CustomUser.EMPLOYMENT_STATUS_CHOICES, required=True)
    work_histories = JSONField(required=True)
    skills_relevance = JSONField(required=True)
    curriculum_relevance = JSONField(required=True)
    perception_further_studies = JSONField(required=True)
    feedback_recommendations = JSONField(required=True)
    alumni_exists = serializers.BooleanField(write_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'middle_name', 'last_name', 'email', 'password', 'confirm_password',
            'school_id', 'government_id', 'program', 'present_address', 'permanent_address',
            'profile_picture', 'contact_number', 'gender', 'birth_date', 'year_graduated',
            'employment_status', 'civil_status', 'alumni_exists', 'mothers_name', 'mothers_occupation',
            'fathers_name', 'fathers_occupation', 'work_histories', 'skills_relevance',
            'curriculum_relevance', 'perception_further_studies', 'feedback_recommendations'
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
        if not data.get('alumni_exists', False):
            raise serializers.ValidationError({"alumni_exists": "You must be a verified alumni to register."})
        return data

    def create(self, validated_data):
        work_histories_data = validated_data.pop('work_histories', [])
        skills_data = validated_data.pop('skills_relevance', {})
        curriculum_data = validated_data.pop('curriculum_relevance', {})
        perception_data = validated_data.pop('perception_further_studies', {})
        feedback_data = validated_data.pop('feedback_recommendations', {})
        validated_data.pop('confirm_password')
        validated_data.pop('alumni_exists', None)

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
            present_address=validated_data['present_address'],
            permanent_address=validated_data['permanent_address'],
            profile_picture=validated_data['profile_picture'],
            contact_number=validated_data['contact_number'],
            gender=validated_data['gender'],
            civil_status=validated_data['civil_status'],
            birth_date=validated_data['birth_date'],
            year_graduated=validated_data['year_graduated'],
            employment_status=validated_data['employment_status'],
            mothers_name=validated_data['mothers_name'],
            mothers_occupation=validated_data['mothers_occupation'],
            fathers_name=validated_data['fathers_name'],
            fathers_occupation=validated_data['fathers_occupation'],
            user_type=3,
            is_approved=False
        )

        for wh_data in work_histories_data:
            skills_data_list = wh_data.pop('skills', [])
            work_history = WorkHistory.objects.create(user=user, **wh_data)
            for skill_data in skills_data_list:
                skill_obj, _ = Skill.objects.get_or_create(name=skill_data['name'])
                work_history.skills.add(skill_obj)

        SkillsRelevance.objects.create(user=user, **skills_data)
        CurriculumRelevance.objects.create(user=user, **curriculum_data)
        PerceptionFurtherStudies.objects.create(user=user, **perception_data)
        FeedbackRecommendations.objects.create(user=user, **feedback_data)
        Profile.objects.create(user=user)
        return user

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
            'school_id', 'government_id', 'program', 'present_address', 'permanent_address',
            'profile_picture', 'contact_number', 'gender', 'user_type', 'is_approved',
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
            present_address=validated_data['present_address'],
            permanent_address=validated_data['permanent_address'],
            profile_picture=validated_data.get('profile_picture'),
            contact_number=validated_data.get('contact_number', ''),
            gender=validated_data.get('gender', ''),
            civil_status=validated_data.get('civil_status', ''),
            user_type=validated_data['user_type'],
            is_approved=validated_data.get('is_approved', False),
            birth_date=validated_data.get('birth_date'),
            year_graduated=validated_data.get('year_graduated'),
            employment_status=validated_data.get('employment_status')
        )
        return user

class ProfileModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ['user']

class ProfileSerializer(serializers.ModelSerializer):
    work_histories = WorkHistorySerializer(many=True)
    skills_relevance = SkillsRelevanceSerializer()
    curriculum_relevance = CurriculumRelevanceSerializer()
    perception_studies = PerceptionFurtherStudiesSerializer()
    feedback = FeedbackRecommendationsSerializer()
    profile = ProfileModelSerializer()

    class Meta:
        model = CustomUser
        exclude = ['password']

    def update(self, instance, validated_data):
        work_histories_data = validated_data.pop('work_histories', [])
        skills_data = validated_data.pop('skills_relevance', {})
        curriculum_data = validated_data.pop('curriculum_relevance', {})
        perception_data = validated_data.pop('perception_studies', {})
        feedback_data = validated_data.pop('feedback', {})
        profile_data = validated_data.pop('profile', {})

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        SkillsRelevance.objects.update_or_create(user=instance, defaults=skills_data)
        CurriculumRelevance.objects.update_or_create(user=instance, defaults=curriculum_data)
        PerceptionFurtherStudies.objects.update_or_create(user=instance, defaults=perception_data)
        FeedbackRecommendations.objects.update_or_create(user=instance, defaults=feedback_data)
        Profile.objects.update_or_create(user=instance, defaults=profile_data)

        instance.work_histories.all().delete()
        for wh_data in work_histories_data:
            skills = wh_data.pop('skills', [])
            work = WorkHistory.objects.create(user=instance, **wh_data)
            for skill_data in skills:
                skill_obj, _ = Skill.objects.get_or_create(**skill_data)
                work.skills.add(skill_obj)

        return instance

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [field.name for field in CustomUser._meta.fields if field.name != 'password']
        
class UserSearchSerializer(serializers.ModelSerializer):
    profile = ProfileModelSerializer(read_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'profile_picture', 'profile']