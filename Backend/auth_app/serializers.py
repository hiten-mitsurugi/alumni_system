from rest_framework import serializers
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
import re
import json

from .models import (
    CustomUser, Skill, UserSkill, WorkHistory, AlumniDirectory, SkillsRelevance,
    CurriculumRelevance, PerceptionFurtherStudies, FeedbackRecommendations, Profile,
    Following, Achievement, Education, Address, FieldPrivacySetting
)

class AddressSerializer(serializers.ModelSerializer):
    """Serializer for the Address model"""
    class Meta:
        model = Address  # Need to import Address model
        exclude = ['user', 'id', 'created_at', 'updated_at', 'normalized_text']

class JSONField(serializers.Field):
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

class AlumniDirectoryCheckSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True)
    middle_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    last_name = serializers.CharField(required=True)
    program = serializers.CharField(required=True)
    birth_date = serializers.DateField(required=True)
    year_graduated = serializers.IntegerField(required=True)
    sex = serializers.ChoiceField(choices=CustomUser.SEX_CHOICES, required=True)

    def validate_sex(self, value):
        valid_choices = [choice[0] for choice in CustomUser.SEX_CHOICES]
        if value not in valid_choices:
            raise serializers.ValidationError(f'"{value}" is not a valid choice.')
        return value

    def validate(self, data):
        from .models import AlumniDirectory  # Move import to top
        
        try:
            query = {
                'first_name__iexact': data['first_name'],
                'last_name__iexact': data['last_name'],
                'birth_date': data['birth_date'],
                'program__iexact': data['program'],
                'year_graduated': data['year_graduated'],
                'sex__iexact': data['sex']  # Changed to case insensitive
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
        fields = ['id', 'first_name', 'middle_name', 'last_name', 'birth_date', 'program', 'year_graduated', 'sex']

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name']

class UserSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSkill
        exclude = ['user']

class WorkHistorySerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, required=False)
    class Meta:
        model = WorkHistory
        fields = [
            'id', 'occupation', 'employing_agency', 'classification', 
            'length_of_service', 'description', 'start_date', 'end_date', 'skills',
            'job_type', 'employment_status', 'how_got_job', 'monthly_income',
            'is_breadwinner', 'college_education_relevant'
        ]

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
    profile = ProfileModelSerializer(read_only=True)
    real_time_status = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = [field.name for field in CustomUser._meta.fields if field.name != 'password'] + ['profile', 'real_time_status']
    
    def get_real_time_status(self, obj):
        """Get real-time status from Redis cache first, then fallback to database"""
        try:
            from .status_cache import UserStatusCache
            
            # First check Redis cache for real-time status
            redis_status = UserStatusCache.get_user_status(obj.id)
            redis_last_seen = UserStatusCache.get_last_seen(obj.id)
            
            # If Redis has valid status data, use it (redis_status can be 'online' or 'offline')
            if redis_status and redis_status in ['online', 'offline']:
                return {
                    'status': redis_status,
                    'last_seen': redis_last_seen.isoformat() if redis_last_seen else None,
                    'is_online': redis_status == 'online'
                }
            
            # Fallback to database profile status
            if hasattr(obj, 'profile') and obj.profile:
                return {
                    'status': obj.profile.status,
                    'last_seen': obj.profile.last_seen.isoformat() if obj.profile.last_seen else None,
                    'is_online': obj.profile.status == 'online'
                }
            else:
                return {
                    'status': 'offline',
                    'last_seen': None,
                    'is_online': False
                }
        except Exception as e:
            # Fallback to offline status if there's any error
            return {
                'status': 'offline',
                'last_seen': None,
                'is_online': False
            }
        
class UserSearchSerializer(serializers.ModelSerializer):
    profile = ProfileModelSerializer(read_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'profile_picture', 'profile']


# LinkedIn-style Social Feature Serializers
class FollowingSerializer(serializers.ModelSerializer):
    follower_name = serializers.CharField(source='follower.get_full_name', read_only=True)
    following_name = serializers.CharField(source='following.get_full_name', read_only=True)
    follower_profile_picture = serializers.ImageField(source='follower.profile_picture', read_only=True)
    following_profile_picture = serializers.ImageField(source='following.profile_picture', read_only=True)
    follower_headline = serializers.CharField(source='follower.profile.headline', read_only=True)
    following_headline = serializers.CharField(source='following.profile.headline', read_only=True)
    
    # Add detailed follower information
    follower_info = serializers.SerializerMethodField()
    following_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Following
        fields = ['id', 'follower', 'following', 'created_at', 'is_mutual', 'status',
                 'follower_name', 'following_name', 'follower_profile_picture', 'following_profile_picture',
                 'follower_headline', 'following_headline', 'follower_info', 'following_info']
        read_only_fields = ['created_at', 'is_mutual']
    
    def get_follower_info(self, obj):
        """Get detailed follower information"""
        # Get present address from Address model
        present_address = obj.follower.get_formatted_present_address()
        
        return {
            'id': obj.follower.id,
            'first_name': obj.follower.first_name,
            'last_name': obj.follower.last_name,
            'username': obj.follower.username,
            'profile_picture': obj.follower.profile_picture.url if obj.follower.profile_picture else None,
            'present_address': present_address,
            'profile': {
                'headline': obj.follower.profile.headline if hasattr(obj.follower, 'profile') else '',
                'present_occupation': obj.follower.profile.present_occupation if hasattr(obj.follower, 'profile') else '',
                'location': obj.follower.profile.location if hasattr(obj.follower, 'profile') else '',
            }
        }
    
    def get_following_info(self, obj):
        """Get detailed following information"""
        # Get present address from Address model
        present_address = obj.following.get_formatted_present_address()
        
        return {
            'id': obj.following.id,
            'first_name': obj.following.first_name,
            'last_name': obj.following.last_name,
            'username': obj.following.username,
            'profile_picture': obj.following.profile_picture.url if obj.following.profile_picture else None,
            'present_address': present_address,
            'profile': {
                'headline': obj.following.profile.headline if hasattr(obj.following, 'profile') else '',
                'present_occupation': obj.following.profile.present_occupation if hasattr(obj.following, 'profile') else '',
                'location': obj.following.profile.location if hasattr(obj.following, 'profile') else '',
            }
        }


class AchievementSerializer(serializers.ModelSerializer):
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
    class Meta:
        model = Education
        fields = ['id', 'institution', 'degree_type', 'field_of_study', 'start_date', 'end_date', 'is_current', 'description', 'user', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']


class EnhancedProfileSerializer(serializers.ModelSerializer):
    """Enhanced Profile serializer with LinkedIn-style features"""
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    connections_count = serializers.SerializerMethodField()
    posts_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    is_followed_by = serializers.SerializerMethodField()
    mutual_connection = serializers.SerializerMethodField()
    
    class Meta:
        model = Profile
        fields = '__all__'
        read_only_fields = ['user', 'timestamp']
    
    def get_followers_count(self, obj):
        return obj.get_followers_count()
    
    def get_following_count(self, obj):
        return obj.get_following_count()
    
    def get_connections_count(self, obj):
        count = obj.get_connections_count()
        print(f"🔍 Backend: get_connections_count for user {obj.user.id} = {count}")
        
        # Debug: Let's see what connections exist
        from .models import Following
        following_records = Following.objects.filter(follower=obj.user)
        follower_records = Following.objects.filter(following=obj.user)
        print(f"🔍 Backend: User {obj.user.id} is following {following_records.count()} users")
        print(f"🔍 Backend: User {obj.user.id} has {follower_records.count()} followers")
        
        for f in following_records:
            print(f"   Following: {f.following.first_name} {f.following.last_name} (status: {f.status})")
        for f in follower_records:
            print(f"   Follower: {f.follower.first_name} {f.follower.last_name} (status: {f.status})")
        
        return count
    
    def get_posts_count(self, obj):
        count = obj.get_posts_count()
        print(f"🔍 Backend: get_posts_count for user {obj.user.id} = {count}")
        return count
    
    def get_is_following(self, obj):
        """Check if current user is following this profile's user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user != obj.user:
            return Following.objects.filter(follower=request.user, following=obj.user).exists()
        return False
    
    def get_is_followed_by(self, obj):
        """Check if this profile's user is following current user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user != obj.user:
            return Following.objects.filter(follower=obj.user, following=request.user).exists()
        return False
    
    def get_mutual_connection(self, obj):
        """Check if there's a mutual connection"""
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user != obj.user:
            return Following.objects.filter(
                follower=request.user, 
                following=obj.user, 
                is_mutual=True
            ).exists()
        return False


class EnhancedUserDetailSerializer(serializers.ModelSerializer):
    """Enhanced User serializer with LinkedIn-style profile features"""
    profile = EnhancedProfileSerializer(read_only=True)
    work_histories = serializers.SerializerMethodField()
    achievements = AchievementSerializer(many=True, read_only=True)
    education = serializers.SerializerMethodField()
    user_skills = UserSkillSerializer(many=True, read_only=True)
    real_time_status = serializers.SerializerMethodField()
    
    def get_work_histories(self, obj):
        """Get work histories deferring the problematic is_current_job field"""
        # Defer the is_current_job field that doesn't exist in database
        work_histories = obj.work_histories.all().defer('is_current_job')
        return WorkHistorySerializer(work_histories, many=True).data
    
    def get_education(self, obj):
        """Explicitly get education records for the user"""
        try:
            from .models import Education
            education_records = Education.objects.filter(user=obj)
            print(f"🔍 DEBUG get_education: Found {education_records.count()} records for user {obj.id}")
            
            if education_records.exists():
                for edu in education_records:
                    print(f"  📚 {edu.field_of_study} at {edu.institution}")
                
                # Use the EducationSerializer defined in this file
                serialized_data = EducationSerializer(education_records, many=True).data
                print(f"🔍 Serialized education data: {serialized_data}")
                return serialized_data
            else:
                print(f"🔍 No education records found for user {obj.id}")
                return []
        except Exception as e:
            print(f"❌ Error in get_education: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def to_representation(self, instance):
        """Override to filter data based on privacy settings"""
        ret = super().to_representation(instance)
        
        # Get the requesting user from context
        request = self.context.get('request')
        requesting_user = request.user if request else None
        
        # If this is the user's own profile, return everything
        if requesting_user and requesting_user.id == instance.id:
            print(f"🔓 Own profile - returning all data for user {instance.id}")
            return ret
        
        # Apply privacy filtering for other users
        print(f"🔒 Filtering privacy for user {instance.id}, viewed by {requesting_user.id if requesting_user else 'anonymous'}")
        
        # Filter individual items based on privacy settings
        ret = self._filter_privacy_items(ret, instance, requesting_user)
        
        return ret
    
    def _filter_privacy_items(self, data, target_user, requesting_user):
        """Filter individual items based on their privacy settings"""
        from .models import FieldPrivacySetting
        
        # Filter education items
        if 'education' in data and data['education']:
            filtered_education = []
            for edu in data['education']:
                field_name = f"education_{edu['id']}"
                visibility = FieldPrivacySetting.get_user_field_visibility(target_user, field_name)
                if self._is_item_visible(visibility, requesting_user, target_user):
                    filtered_education.append(edu)
                else:
                    print(f"🚫 Hiding education {edu['id']} (visibility: {visibility})")
            data['education'] = filtered_education
        
        # Filter work histories
        if 'work_histories' in data and data['work_histories']:
            filtered_work = []
            for work in data['work_histories']:
                field_name = f"experience_{work['id']}"
                visibility = FieldPrivacySetting.get_user_field_visibility(target_user, field_name)
                if self._is_item_visible(visibility, requesting_user, target_user):
                    filtered_work.append(work)
                else:
                    print(f"🚫 Hiding work experience {work['id']} (visibility: {visibility})")
            data['work_histories'] = filtered_work
        
        # Filter achievements
        if 'achievements' in data and data['achievements']:
            filtered_achievements = []
            for achievement in data['achievements']:
                field_name = f"achievement_{achievement['id']}"
                visibility = FieldPrivacySetting.get_user_field_visibility(target_user, field_name)
                if self._is_item_visible(visibility, requesting_user, target_user):
                    filtered_achievements.append(achievement)
                else:
                    print(f"🚫 Hiding achievement {achievement['id']} (visibility: {visibility})")
            data['achievements'] = filtered_achievements
        
        # Filter user skills
        if 'user_skills' in data and data['user_skills']:
            filtered_skills = []
            for skill in data['user_skills']:
                field_name = f"skill_{skill['id']}"
                visibility = FieldPrivacySetting.get_user_field_visibility(target_user, field_name)
                if self._is_item_visible(visibility, requesting_user, target_user):
                    filtered_skills.append(skill)
                else:
                    print(f"🚫 Hiding skill {skill['id']} (visibility: {visibility})")
            data['user_skills'] = filtered_skills
        
        return data
    
    def _is_item_visible(self, visibility, requesting_user, target_user):
        """Check if an item should be visible based on privacy settings"""
        if visibility == 'everyone':
            return True
        elif visibility == 'only_me':
            return False
        elif visibility == 'connections_only':
            if not requesting_user or requesting_user.is_anonymous:
                return False
            # Check if users are connected
            from .models import Following
            return Following.objects.filter(
                follower=requesting_user,
                following=target_user,
                is_mutual=True,
                status='accepted'
            ).exists()
        return False
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'middle_name',
            'user_type', 'sex', 'gender', 'civil_status', 'employment_status',
            'is_approved', 'profile_picture', 'government_id', 'program',
            'contact_number', 'birth_date', 'year_graduated', 'mothers_name',
            'mothers_occupation', 'fathers_name', 'fathers_occupation',
            'is_active', 'is_staff', 'is_superuser', 'last_login', 'date_joined',
            'profile', 'work_histories', 'achievements', 'education', 'user_skills', 'real_time_status'
        ]
    
    def get_real_time_status(self, obj):
        """Get real-time status from Redis cache first, then fallback to database"""
        try:
            from .status_cache import UserStatusCache
            
            # First check Redis cache for real-time status
            redis_status = UserStatusCache.get_user_status(obj.id)
            redis_last_seen = UserStatusCache.get_last_seen(obj.id)
            
            # If Redis has valid status data, use it
            if redis_status and redis_status in ['online', 'offline']:
                return {
                    'status': redis_status,
                    'last_seen': redis_last_seen.isoformat() if redis_last_seen else None,
                    'is_online': redis_status == 'online'
                }
            
            # Fallback to database profile status
            if hasattr(obj, 'profile') and obj.profile:
                return {
                    'status': obj.profile.status,
                    'last_seen': obj.profile.last_seen.isoformat() if obj.profile.last_seen else None,
                    'is_online': obj.profile.status == 'online'
                }
            else:
                return {
                    'status': 'offline',
                    'last_seen': None,
                    'is_online': False
                }
        except Exception as e:
            # Fallback to offline status if there's any error
            return {
                'status': 'offline',
                'last_seen': None,
                'is_online': False
            }


class FieldPrivacySettingSerializer(serializers.ModelSerializer):
    """Serializer for field privacy settings"""
    class Meta:
        model = FieldPrivacySetting
        fields = ['field_name', 'visibility']
        
    def validate_visibility(self, value):
        """Validate visibility choices"""
        valid_choices = [choice[0] for choice in FieldPrivacySetting.VISIBILITY_CHOICES]
        if value not in valid_choices:
            raise serializers.ValidationError(f'"{value}" is not a valid visibility choice.')
        return value


class ProfileFieldUpdateSerializer(serializers.Serializer):
    """Serializer for updating individual profile fields"""
    field_name = serializers.CharField(max_length=100)
    field_value = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    visibility = serializers.ChoiceField(
        choices=FieldPrivacySetting.VISIBILITY_CHOICES, 
        required=False,
        default='connections_only'
    )
    target_user_id = serializers.IntegerField(required=False)