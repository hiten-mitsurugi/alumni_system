from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        (1, 'Super Admin'),
        (2, 'Admin'),
        (3, 'Alumni'),
    )

    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('prefer_not_to_say', 'Prefer not to say'),
    )

    CIVIL_STATUS_CHOICES = (
        ('single', 'Single'),
        ('married', 'Married'),
        ('widow', 'Widow'),
    )

    EMPLOYMENT_STATUS_CHOICES = (
        ('employed_locally', 'Employed Locally'),
        ('employed_internationally', 'Employed Internationally'),
        ('self_employed', 'Self-Employed'),
        ('unemployed', 'Unemployed'),
    )

    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, default=3)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True, null=True)
    civil_status = models.CharField(max_length=20, choices=CIVIL_STATUS_CHOICES, blank=True, null=True)
    employment_status = models.CharField(max_length=100, choices=EMPLOYMENT_STATUS_CHOICES, blank=True, null=True)
    
    is_approved = models.BooleanField(default=False)
    email = models.EmailField(_('email address'), unique=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    middle_name = models.CharField(max_length=150, blank=True, null=True)
    school_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    government_id = models.FileField(upload_to='government_ids/', null=True, blank=True)
    program = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    year_graduated = models.PositiveIntegerField(blank=True, null=True)

    REQUIRED_FIELDS = ['email', 'school_id', 'first_name', 'last_name', 'password', 'program']

    class Meta:
        indexes = [
            models.Index(fields=['user_type', 'is_approved']),
            models.Index(fields=['school_id']),
        ]

    def __str__(self):
        return self.username

class AlumniDirectory(models.Model):
    first_name = models.CharField(max_length=150)
    middle_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150)
    birth_date = models.DateField()
    school_id = models.CharField(max_length=50, unique=True)
    program = models.CharField(max_length=100)
    year_graduated = models.PositiveIntegerField()
    gender = models.CharField(max_length=20, choices=CustomUser.GENDER_CHOICES)
    class Meta:
        indexes = [
            models.Index(fields=['school_id']),
            models.Index(fields=['first_name', 'last_name']),
        ]
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.school_id})"

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    def __str__(self):
        return self.name

class WorkHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='work_histories')
    company_name = models.CharField(max_length=255)
    company_address = models.TextField()
    position = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    skills = models.ManyToManyField(Skill, related_name='work_histories')
    def __str__(self):
        return f'{self.company_name} - {self.position}'

class SurveyCategory(models.Model):
    """Categories for organizing survey questions"""
    name = models.CharField(max_length=200)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = "Survey Categories"
    
    def __str__(self):
        return self.name

class SurveyQuestion(models.Model):
    """Dynamic survey questions that can be managed by superadmin"""
    QUESTION_TYPES = [
        ('text', 'Text Input'),
        ('textarea', 'Text Area'),
        ('select', 'Single Select'),
        ('radio', 'Radio Button'),
        ('checkbox', 'Multiple Select'),
        ('number', 'Number'),
        ('email', 'Email'),
        ('date', 'Date'),
        ('rating', 'Rating Scale'),
        ('yes_no', 'Yes/No'),
    ]
    
    category = models.ForeignKey(SurveyCategory, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    options = models.JSONField(default=list, blank=True, help_text="For select, radio, checkbox questions")
    is_required = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category__order', 'order', 'id']
    
    def __str__(self):
        return f"{self.category.name}: {self.question_text[:50]}..."

class SurveyResponse(models.Model):
    """Stores survey responses from users during registration"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='survey_responses')
    question = models.ForeignKey(SurveyQuestion, on_delete=models.CASCADE, null=True, blank=True)
    response_text = models.TextField(blank=True, null=True)
    response_number = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    response_date = models.DateField(blank=True, null=True)
    response_json = models.JSONField(blank=True, null=True, help_text="For multiple choice answers")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'question']
    
    def __str__(self):
        if self.question:
            return f"{self.user.email} - {self.question.question_text[:30]}..."
        return f"{self.user.email} - No question"