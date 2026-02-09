"""
User registration and creation serializers.
Contains RegisterSerializer and UserCreateSerializer for user account creation.
"""
from rest_framework import serializers
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

from ..models import (
    CustomUser, Skill, WorkHistory, Profile, Address,
    SkillsRelevance, CurriculumRelevance, PerceptionFurtherStudies, 
    FeedbackRecommendations
)
from .base_serializers import JSONField


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration with comprehensive profile data"""
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    gender = serializers.ChoiceField(choices=CustomUser.GENDER_CHOICES, required=True)
    civil_status = serializers.ChoiceField(choices=CustomUser.CIVIL_STATUS_CHOICES, required=True)
    employment_status = serializers.ChoiceField(choices=CustomUser.EMPLOYMENT_STATUS_CHOICES, required=True)
    work_histories = JSONField(required=False)  # Made optional for dynamic surveys
    skills_relevance = JSONField(required=False)  # Made optional for dynamic surveys
    curriculum_relevance = JSONField(required=False)  # Made optional for dynamic surveys
    perception_further_studies = JSONField(required=False)  # Made optional for dynamic surveys
    feedback_recommendations = JSONField(required=False)  # Made optional for dynamic surveys
    survey_responses = JSONField(required=False)  # New field for dynamic survey responses
    alumni_exists = serializers.BooleanField(write_only=True)
    
    # Address fields using the new Address model
    present_address_data = JSONField(required=False)
    permanent_address_data = JSONField(required=False)

    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'middle_name', 'last_name', 'email', 'password', 'confirm_password',
            'government_id', 'program', 'profile_picture', 'contact_number', 'gender', 'birth_date', 
            'year_graduated', 'employment_status', 'civil_status', 'alumni_exists', 'mothers_name', 
            'mothers_occupation', 'fathers_name', 'fathers_occupation', 'work_histories', 
            'skills_relevance', 'curriculum_relevance', 'perception_further_studies', 
            'feedback_recommendations', 'survey_responses', 'present_address_data', 'permanent_address_data'
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
        survey_responses_data = validated_data.pop('survey_responses', [])
        present_address_data = validated_data.pop('present_address_data', {})
        permanent_address_data = validated_data.pop('permanent_address_data', {})
        validated_data.pop('confirm_password')
        validated_data.pop('alumni_exists', None)

        if not validated_data.get('middle_name'):
            validated_data['middle_name'] = ''

        # Create user without address fields (they no longer exist on CustomUser)
        user = CustomUser.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            middle_name=validated_data['middle_name'],
            last_name=validated_data['last_name'],
            government_id=validated_data['government_id'],
            program=validated_data['program'],
            profile_picture=validated_data['profile_picture'],
            contact_number=validated_data['contact_number'],
            gender=validated_data.get('gender'),
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

        # Create Address objects using the new Address model
        if present_address_data:
            Address.objects.create(
                user=user,
                address_category='present',
                **present_address_data
            )
        
        if permanent_address_data:
            Address.objects.create(
                user=user,
                address_category='permanent',
                **permanent_address_data
            )

        # Handle work histories if provided (backward compatibility)
        for wh_data in work_histories_data:
            skills_data_list = wh_data.pop('skills', [])
            work_history = WorkHistory.objects.create(user=user, **wh_data)
            for skill_data in skills_data_list:
                skill_obj, _ = Skill.objects.get_or_create(name=skill_data['name'])
                work_history.skills.add(skill_obj)

        # Handle legacy questionnaire data if provided (backward compatibility)
        if skills_data:
            SkillsRelevance.objects.create(user=user, **skills_data)
        if curriculum_data:
            CurriculumRelevance.objects.create(user=user, **curriculum_data)
        if perception_data:
            PerceptionFurtherStudies.objects.create(user=user, **perception_data)
        if feedback_data:
            FeedbackRecommendations.objects.create(user=user, **feedback_data)

        # Handle dynamic survey responses
        if survey_responses_data:
            from survey_app.models import SurveyResponse, SurveyQuestion, SurveyTemplate
            
            # Determine which template (form) these responses belong to
            form_template = None
            if survey_responses_data:
                try:
                    first_question = SurveyQuestion.objects.select_related('category').get(
                        id=survey_responses_data[0]['question']
                    )
                    # Find the registration template (default template or one containing this category)
                    form_template = SurveyTemplate.objects.filter(
                        categories=first_question.category,
                        is_active=True
                    ).first()
                except (SurveyQuestion.DoesNotExist, IndexError):
                    pass
            
            for response_data in survey_responses_data:
                try:
                    question = SurveyQuestion.objects.get(id=response_data['question'])
                    SurveyResponse.objects.create(
                        user=user,
                        question=question,
                        response_data=response_data['response_data'],
                        form=form_template  # Link to template
                    )
                except SurveyQuestion.DoesNotExist:
                    # Log error but don't fail registration
                    print(f"Warning: Survey question {response_data['question']} not found")

        Profile.objects.create(user=user)
        return user


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating users (admin functionality)"""
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    government_id = serializers.FileField(allow_null=True, required=False)
    profile_picture = serializers.ImageField(allow_null=True, required=False)
    user_type = serializers.ChoiceField(choices=CustomUser.USER_TYPE_CHOICES)
    civil_status = serializers.ChoiceField(choices=CustomUser.CIVIL_STATUS_CHOICES, required=False)

    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'middle_name', 'last_name', 'email', 'password',
            'government_id', 'program', 'profile_picture', 'contact_number', 'sex', 
            'user_type', 'is_approved', 'birth_date', 'year_graduated', 'employment_status', 
            'civil_status'
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
