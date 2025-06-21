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