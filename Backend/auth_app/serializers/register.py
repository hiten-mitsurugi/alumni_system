from rest_framework import serializers
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from ..models import CustomUser, Profile, WorkHistory, Skill, SkillsRelevance, CurriculumRelevance, PerceptionFurtherStudies, FeedbackRecommendations
from .base import JSONField, AddressSerializer


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    sex = serializers.ChoiceField(choices=CustomUser.GENDER_CHOICES, required=True)
    civil_status = serializers.ChoiceField(choices=CustomUser.CIVIL_STATUS_CHOICES, required=True)
    employment_status = serializers.ChoiceField(choices=CustomUser.EMPLOYMENT_STATUS_CHOICES, required=True)
    work_histories = JSONField(required=False)  # Made optional for dynamic surveys
    skills_relevance = JSONField(required=False)  # Made optional for dynamic surveys
    curriculum_relevance = JSONField(required=False)  # Made optional for dynamic surveys
    perception_further_studies = JSONField(required=False)  # Made optional for dynamic surveys
    feedback_recommendations = JSONField(required=False)  # Made optional for dynamic surveys
    survey_responses = JSONField(required=False)  # New field for dynamic survey responses
    alumni_exists = serializers.BooleanField(write_only=True)
    
    # Structured address fields
    present_address_data = AddressSerializer(required=False, write_only=True)
    permanent_address_data = AddressSerializer(required=False, write_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'middle_name', 'last_name', 'email', 'password', 'confirm_password',
            'government_id', 'program', 'present_address', 'permanent_address',
            'profile_picture', 'contact_number', 'sex', 'birth_date', 'year_graduated',
            'employment_status', 'civil_status', 'alumni_exists', 'mothers_name', 'mothers_occupation',
            'fathers_name', 'fathers_occupation', 'work_histories', 'skills_relevance',
            'curriculum_relevance', 'perception_further_studies', 'feedback_recommendations',
            'survey_responses', 'present_address_data', 'permanent_address_data'
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
        survey_responses_data = validated_data.pop('survey_responses', [])  # New field
        present_address_data = validated_data.pop('present_address_data', {})
        permanent_address_data = validated_data.pop('permanent_address_data', {})
        validated_data.pop('confirm_password')
        validated_data.pop('alumni_exists', None)

        if not validated_data.get('middle_name'):
            validated_data['middle_name'] = ''

        # Prepare structured address fields for CustomUser
        address_fields = {}
        
        # Handle present address data
        if present_address_data:
            address_fields.update({
                'present_address_type': present_address_data.get('address_type', 'philippines'),
                'present_region_code': present_address_data.get('region_code', ''),
                'present_region_name': present_address_data.get('region_name', ''),
                'present_province_code': present_address_data.get('province_code', ''),
                'present_province_name': present_address_data.get('province_name', ''),
                'present_city_code': present_address_data.get('city_code', ''),
                'present_city_name': present_address_data.get('city_name', ''),
                'present_barangay': present_address_data.get('barangay', ''),
                'present_street_address': present_address_data.get('street_address', ''),
                'present_postal_code': present_address_data.get('postal_code', ''),
                'present_country': present_address_data.get('country', ''),
                'present_full_address': present_address_data.get('full_address', ''),
            })
        
        # Handle permanent address data
        if permanent_address_data:
            address_fields.update({
                'permanent_address_type': permanent_address_data.get('address_type', 'philippines'),
                'permanent_region_code': permanent_address_data.get('region_code', ''),
                'permanent_region_name': permanent_address_data.get('region_name', ''),
                'permanent_province_code': permanent_address_data.get('province_code', ''),
                'permanent_province_name': permanent_address_data.get('province_name', ''),
                'permanent_city_code': permanent_address_data.get('city_code', ''),
                'permanent_city_name': permanent_address_data.get('city_name', ''),
                'permanent_barangay': permanent_address_data.get('barangay', ''),
                'permanent_street_address': permanent_address_data.get('street_address', ''),
                'permanent_postal_code': permanent_address_data.get('postal_code', ''),
                'permanent_country': permanent_address_data.get('country', ''),
                'permanent_full_address': permanent_address_data.get('full_address', ''),
            })

        user = CustomUser.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            middle_name=validated_data['middle_name'],
            last_name=validated_data['last_name'],
            government_id=validated_data['government_id'],
            program=validated_data['program'],
            present_address=validated_data.get('present_address', ''),  # Legacy field
            permanent_address=validated_data.get('permanent_address', ''),  # Legacy field
            profile_picture=validated_data['profile_picture'],
            contact_number=validated_data['contact_number'],
            sex=validated_data['sex'],
            civil_status=validated_data['civil_status'],
            birth_date=validated_data['birth_date'],
            year_graduated=validated_data['year_graduated'],
            employment_status=validated_data['employment_status'],
            mothers_name=validated_data['mothers_name'],
            mothers_occupation=validated_data['mothers_occupation'],
            fathers_name=validated_data['fathers_name'],
            fathers_occupation=validated_data['fathers_occupation'],
            user_type=3,
            is_approved=False,
            **address_fields  # Add structured address fields
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
            from survey_app.models import SurveyResponse, SurveyQuestion
            for response_data in survey_responses_data:
                try:
                    question = SurveyQuestion.objects.get(id=response_data['question'])
                    SurveyResponse.objects.create(
                        user=user,
                        question=question,
                        response_data=response_data['response_data']
                    )
                except SurveyQuestion.DoesNotExist:
                    # Log error but don't fail registration
                    print(f"Warning: Survey question {response_data['question']} not found")

        Profile.objects.create(user=user)
        return user