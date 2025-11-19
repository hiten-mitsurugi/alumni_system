from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import SurveyCategory, SurveyQuestion, SurveyResponse, SurveyTemplate

User = get_user_model()


class SurveyCategorySerializer(serializers.ModelSerializer):
    """Serializer for survey categories"""
    active_questions_count = serializers.ReadOnlyField()
    total_questions_count = serializers.ReadOnlyField()
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    depends_on_category_name = serializers.CharField(source='depends_on_category.name', read_only=True)

    class Meta:
        model = SurveyCategory
        fields = [
            'id', 'name', 'description', 'order', 'is_active', 'include_in_registration',
            'depends_on_category', 'depends_on_category_name', 
            'depends_on_question_text', 'depends_on_value',
            'active_questions_count', 'total_questions_count', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class SurveyQuestionSerializer(serializers.ModelSerializer):
    """Serializer for survey questions"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    response_count = serializers.ReadOnlyField()
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    depends_on_question_id = serializers.IntegerField(source='depends_on_question.id', read_only=True)

    class Meta:
        model = SurveyQuestion
        fields = [
            'id', 'category', 'category_name', 'question_text', 'question_type',
            'placeholder_text', 'help_text', 'options', 'is_required',
            'min_value', 'max_value', 'max_length', 'order', 'is_active',
            'depends_on_question', 'depends_on_question_id', 'depends_on_value', 'branching',
            'response_count', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

    def validate_options(self, value):
        """Validate options field based on question type"""
        question_type = self.initial_data.get('question_type')
        
        if question_type in ['radio', 'checkbox', 'select']:
            if not value or not isinstance(value, list) or len(value) < 2:
                raise serializers.ValidationError(
                    "Choice questions must have at least 2 options as a list."
                )
        
        return value

    def validate(self, data):
        """Cross-field validation"""
        min_val = data.get('min_value')
        max_val = data.get('max_value')
        
        if min_val is not None and max_val is not None and min_val >= max_val:
            raise serializers.ValidationError(
                "Minimum value must be less than maximum value."
            )
        
        return data


class SurveyQuestionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing questions"""
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = SurveyQuestion
        fields = [
            'id', 'category', 'category_name', 'question_text', 
            'question_type', 'is_required', 'order', 'is_active'
        ]


class SurveyResponseSerializer(serializers.ModelSerializer):
    """Serializer for survey responses"""
    question_text = serializers.CharField(source='question.question_text', read_only=True)
    question_type = serializers.CharField(source='question.question_type', read_only=True)
    category_name = serializers.CharField(source='question.category.name', read_only=True)
    display_value = serializers.CharField(source='get_display_value', read_only=True)

    class Meta:
        model = SurveyResponse
        fields = [
            'id', 'user', 'question', 'question_text', 'question_type',
            'category_name', 'response_data', 'display_value',
            'submitted_at', 'updated_at', 'form'
        ]
        read_only_fields = ['user', 'submitted_at', 'updated_at']


class SurveyResponseDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for survey responses with nested user and question data"""
    user = serializers.SerializerMethodField()
    question = serializers.SerializerMethodField()
    display_value = serializers.CharField(source='get_display_value', read_only=True)

    class Meta:
        model = SurveyResponse
        fields = [
            'id', 'user', 'question', 'response_data', 'display_value',
            'submitted_at', 'updated_at', 'form'
        ]
        read_only_fields = ['submitted_at', 'updated_at']

    def get_user(self, obj):
        """Return user details"""
        if obj.user:
            return {
                'id': obj.user.id,
                'email': obj.user.email,
                'full_name': obj.user.get_full_name() if hasattr(obj.user, 'get_full_name') else f"{obj.user.first_name} {obj.user.last_name}".strip(),
                'first_name': obj.user.first_name,
                'last_name': obj.user.last_name
            }
        return None

    def get_question(self, obj):
        """Return question details with category"""
        if obj.question:
            return {
                'id': obj.question.id,
                'question_text': obj.question.question_text,
                'question_type': obj.question.question_type,
                'is_required': obj.question.is_required,
                'category': {
                    'id': obj.question.category.id,
                    'name': obj.question.category.name
                } if obj.question.category else None
            }
        return None

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        # Get IP address from request
        request = self.context.get('request')
        if request:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                validated_data['ip_address'] = x_forwarded_for.split(',')[0]
            else:
                validated_data['ip_address'] = request.META.get('REMOTE_ADDR')
        
        return super().create(validated_data)


class SurveyResponseSubmissionSerializer(serializers.Serializer):
    """Serializer for bulk response submission"""
    responses = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of responses in format: [{'question_id': 1, 'response_data': 'answer'}]"
    )

    def validate_responses(self, value):
        """Validate the responses format"""
        if not value:
            raise serializers.ValidationError("At least one response is required.")
        
        for response in value:
            if 'question_id' not in response:
                raise serializers.ValidationError("Each response must have a 'question_id'.")
            if 'response_data' not in response:
                raise serializers.ValidationError("Each response must have 'response_data'.")
        
        return value

    def create(self, validated_data):
        """Create multiple responses"""
        user = self.context['request'].user
        responses = validated_data['responses']
        
        created_responses = []
        for response_data in responses:
            question_id = response_data['question_id']
            response_value = response_data['response_data']
            
            try:
                question = SurveyQuestion.objects.get(id=question_id, is_active=True)
                
                # Update or create response
                response_obj, created = SurveyResponse.objects.update_or_create(
                    user=user,
                    question=question,
                    defaults={
                        'response_data': response_value,
                        'ip_address': self.context.get('ip_address')
                    }
                )
                created_responses.append(response_obj)
                
            except SurveyQuestion.DoesNotExist:
                raise serializers.ValidationError(f"Question with ID {question_id} not found or inactive.")
        
        return created_responses


class ActiveSurveyQuestionsSerializer(serializers.ModelSerializer):
    """Serializer for active survey questions (for alumni to answer)"""
    category = SurveyCategorySerializer(read_only=True)
    user_response = serializers.SerializerMethodField()
    # Include conditional logic fields for Survey.vue to evaluate visibility
    depends_on_question_id = serializers.IntegerField(
        source='depends_on_question.id', 
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = SurveyQuestion
        fields = [
            'id', 'category', 'question_text', 'question_type',
            'placeholder_text', 'help_text', 'options', 'is_required',
            'min_value', 'max_value', 'max_length', 'order', 'user_response',
            'depends_on_question_id', 'depends_on_value'  # Conditional logic fields
        ]

    def get_user_response(self, obj):
        """Get current user's response to this question"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        
        try:
            response = SurveyResponse.objects.get(user=request.user, question=obj)
            return {
                'id': response.id,
                'response_data': response.response_data,
                'submitted_at': response.submitted_at,
                'display_value': response.get_display_value()
            }
        except SurveyResponse.DoesNotExist:
            return None


class SurveyAnalyticsSerializer(serializers.Serializer):
    """Serializer for survey analytics data"""
    total_questions = serializers.IntegerField()
    total_responses = serializers.IntegerField()
    total_users_responded = serializers.IntegerField()
    completion_rate = serializers.FloatField()
    category_stats = serializers.ListField()
    question_stats = serializers.ListField()


class SurveyTemplateSerializer(serializers.ModelSerializer):
    """Serializer for survey templates"""
    categories = SurveyCategorySerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=SurveyCategory.objects.filter(is_active=True),
        write_only=True,
        required=False,
        allow_empty=True,
        source='categories'
    )
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = SurveyTemplate
        fields = [
            'id', 'name', 'description', 'categories', 'category_ids',
            'is_active', 'is_default', 'is_published', 'accepting_responses',
            'start_at', 'end_at', 'confirmation_message', 'form_settings',
            'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def create(self, validated_data):
        # created_by is set in the view's perform_create method
        # Only set it here if not already set
        if 'created_by' not in validated_data:
            validated_data['created_by'] = self.context.get('request').user
        
        categories = validated_data.pop('categories', [])
        
        template = super().create(validated_data)
        
        # Set categories with order
        if categories:
            for i, category in enumerate(categories):
                template.surveytemplatecategory_set.create(category=category, order=i)
        
        return template

    def update(self, instance, validated_data):
        # Handle categories separately
        categories = validated_data.pop('categories', None)
        
        # Update other fields
        instance = super().update(instance, validated_data)
        
        # Update categories if provided
        if categories is not None:
            # Clear existing categories
            instance.surveytemplatecategory_set.all().delete()
            
            # Add new categories with order
            for i, category in enumerate(categories):
                instance.surveytemplatecategory_set.create(category=category, order=i)
        
        return instance
