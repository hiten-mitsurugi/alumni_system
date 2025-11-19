from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
import json


class SurveyCategory(models.Model):
    """Categories to organize survey questions (e.g., Personal Info, Work History)"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0, help_text="Order for display (lower numbers first)")
    is_active = models.BooleanField(default=True)
    include_in_registration = models.BooleanField(
        default=False,
        help_text="Include this category in the public registration survey"
    )
    
    # Google Forms-like page semantics
    page_break = models.BooleanField(
        default=True,
        help_text="Treat this category as a separate page/section in multi-page surveys"
    )
    page_title = models.CharField(
        max_length=200, 
        blank=True,
        help_text="Optional page title (defaults to category name if blank)"
    )
    page_description = models.TextField(
        blank=True,
        help_text="Optional description shown at the top of this page/section"
    )
    
    # Category-level conditional logic
    depends_on_category = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Category this depends on for conditional display"
    )
    depends_on_question_text = models.CharField(
        max_length=500,
        blank=True,
        help_text="Specific question text within the dependency category"
    )
    depends_on_value = models.TextField(
        blank=True,
        help_text="Value that triggers display of this category (JSON for multiple values)"
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        limit_choices_to={'user_type__in': [1, 2]}  # Only Admins/Super Admins
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = "Survey Categories"

    def __str__(self):
        return self.name

    @property
    def active_questions_count(self):
        return self.questions.filter(is_active=True).count()
        
    @property 
    def total_questions_count(self):
        return self.questions.count()


class SurveyQuestion(models.Model):
    """Dynamic survey questions with flexible types"""
    QUESTION_TYPES = [
        ('text', 'Text Input'),
        ('textarea', 'Long Text Area'),
        ('radio', 'Single Choice (Radio)'),
        ('checkbox', 'Multiple Choice (Checkbox)'),
        ('select', 'Dropdown Select'),
        ('number', 'Number Input'),
        ('year', 'Year (YYYY)'),
        ('email', 'Email Input'),
        ('date', 'Date Picker'),
        ('rating', 'Rating Scale (1-5)'),
        ('yes_no', 'Yes/No Question'),
        ('file', 'File Upload'),
    ]

    category = models.ForeignKey(
        SurveyCategory, 
        on_delete=models.CASCADE, 
        related_name='questions'
    )
    question_text = models.TextField(help_text="The question text that will be displayed")
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    placeholder_text = models.CharField(max_length=255, blank=True, help_text="Placeholder text for input fields")
    help_text = models.CharField(max_length=500, blank=True, help_text="Additional help text for the question")
    
    # Options for choice-based questions (radio, checkbox, select)
    options = models.JSONField(
        blank=True, 
        null=True,
        help_text="JSON array of options for choice questions. Example: ['Option 1', 'Option 2']"
    )
    
    # Validation settings
    is_required = models.BooleanField(default=False)
    min_value = models.IntegerField(blank=True, null=True, help_text="Minimum value for number/rating questions")
    max_value = models.IntegerField(blank=True, null=True, help_text="Maximum value for number/rating questions")
    max_length = models.IntegerField(blank=True, null=True, help_text="Maximum character length for text inputs")
    
    # Display settings
    order = models.PositiveIntegerField(default=0, help_text="Order within category (lower numbers first)")
    is_active = models.BooleanField(default=True)
    
    # Conditional Logic Fields
    depends_on_question = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Question this depends on for conditional display"
    )
    depends_on_value = models.TextField(
        blank=True,
        help_text="Value that triggers display of this question (JSON for multiple values)"
    )
    
    # Branching configuration: map option/value -> target category id or action
    branching = models.JSONField(
        null=True,
        blank=True,
        default=dict,
        help_text="JSON mapping for branching (option -> target_category_id or action)"
    )
    # Google Forms-like branching (go-to-section based on answer)
    branching = models.JSONField(
        blank=True,
        null=True,
        help_text="Branching logic: map answer options to target categories. Example: {'option_1': {'action': 'goto', 'target_category_id': 5}, 'default': {'action': 'continue'}}"
    )
    
    # Audit fields
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        limit_choices_to={'user_type__in': [1, 2]}  # Only Admins/Super Admins
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category__order', 'order', 'question_text']
        unique_together = ['category', 'question_text']  # Prevent duplicate questions in same category

    def __str__(self):
        return f"{self.category.name}: {self.question_text[:50]}"

    def clean(self):
        """Validate question configuration"""
        from django.core.exceptions import ValidationError
        
        # Validate that choice questions have options
        if self.question_type in ['radio', 'checkbox', 'select']:
            if not self.options or not isinstance(self.options, list) or len(self.options) < 2:
                raise ValidationError("Choice questions must have at least 2 options")
        
        # Validate min/max values
        if self.min_value is not None and self.max_value is not None:
            if self.min_value >= self.max_value:
                raise ValidationError("Minimum value must be less than maximum value")

    @property
    def response_count(self):
        """Count how many users have responded to this question"""
        return self.responses.count()

    def get_options_list(self):
        """Get options as a list, handling various input formats"""
        if not self.options:
            return []
        if isinstance(self.options, str):
            try:
                return json.loads(self.options)
            except json.JSONDecodeError:
                return []
        return self.options if isinstance(self.options, list) else []


class SurveyResponse(models.Model):
    """Store user responses to survey questions"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='survey_responses'
    )
    question = models.ForeignKey(
        SurveyQuestion, 
        on_delete=models.CASCADE,
        related_name='responses'
    )
    
    # Flexible response storage - can handle any data type
    response_data = models.JSONField(help_text="Stores the actual response data")
    
    # Metadata
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    # Optional reference to the form/template this response belongs to
    form = models.ForeignKey(
        'SurveyTemplate',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='form_responses'
    )

    class Meta:
        unique_together = ['user', 'question']  # One response per user per question
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.user.email} - {self.question.question_text[:30]}"

    @property
    def response_value(self):
        """Get the actual response value in a readable format"""
        if not self.response_data:
            return None
        
        # Handle different response types
        if isinstance(self.response_data, dict):
            return self.response_data.get('value', self.response_data)
        return self.response_data

    def get_display_value(self):
        """Get a human-readable display value"""
        value = self.response_value
        if value is None:
            return "No response"
        
        question_type = self.question.question_type
        
        if question_type == 'yes_no':
            return "Yes" if value else "No"
        elif question_type == 'rating':
            return f"{value}/5"
        elif question_type in ['radio', 'select']:
            return str(value)
        elif question_type == 'checkbox':
            if isinstance(value, list):
                return ", ".join(str(v) for v in value)
            return str(value)
        else:
            return str(value)


class SurveyTemplate(models.Model):
    """Templates for different types of surveys (e.g., Registration Survey, Alumni Tracer)
    Now also acts as a Form with Google Forms-like publishing and response settings"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    categories = models.ManyToManyField(SurveyCategory, through='SurveyTemplateCategory')
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False, help_text="Default template for new registrations")
    
    # Google Forms-like form publishing settings
    is_published = models.BooleanField(
        default=False,
        help_text="Whether this form is published and accepting responses"
    )
    accepting_responses = models.BooleanField(
        default=True,
        help_text="Whether responses are currently accepted"
    )
    start_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Optional start datetime for accepting responses"
    )
    end_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Optional end datetime for accepting responses"
    )
    confirmation_message = models.TextField(
        blank=True,
        default='',
        help_text="Message shown to respondents after submission"
    )
    form_settings = models.JSONField(
        default=dict,
        blank=True,
        null=True,
        help_text="Flexible JSON settings for the form"
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        limit_choices_to={'user_type__in': [1, 2]}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Ensure only one default template
        if self.is_default:
            SurveyTemplate.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


    # New form-like settings (additive, nullable/defaulted for safe migrations)
    is_published = models.BooleanField(default=False, help_text="Whether this form is published and accepting responses")
    accepting_responses = models.BooleanField(default=True, help_text="Whether responses are currently accepted")
    start_at = models.DateTimeField(null=True, blank=True, help_text="Optional start datetime for accepting responses")
    end_at = models.DateTimeField(null=True, blank=True, help_text="Optional end datetime for accepting responses")
    confirmation_message = models.TextField(blank=True, default='', help_text="Message shown to respondents after submission")
    form_settings = models.JSONField(null=True, blank=True, default=dict, help_text="Flexible JSON settings for the form")


class SurveyTemplateCategory(models.Model):
    """Through model for SurveyTemplate and SurveyCategory relationship"""
    template = models.ForeignKey(SurveyTemplate, on_delete=models.CASCADE)
    category = models.ForeignKey(SurveyCategory, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        unique_together = ['template', 'category']

    def __str__(self):
        return f"{self.template.name} - {self.category.name}"
