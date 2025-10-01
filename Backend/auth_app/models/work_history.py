from django.db import models
from django.conf import settings
from .skill import Skill


class WorkHistory(models.Model):
    EMPLOYMENT_STATUS_CHOICES = (
        ('employed_locally', 'Employed Locally'),
        ('employed_internationally', 'Employed Internationally'),
        ('self_employed', 'Self-Employed'),
        ('unemployed', 'Unemployed'),
        ('retired', 'Retired'),
    )
    CLASSIFICATION_CHOICES = (
        ('government', 'Government'),
        ('private', 'Private'),
        ('ngo', 'NGO'),
        ('freelance', 'Freelance'),
        ('business_owner', 'Business Owner'),
    )
    INCOME_CHOICES = (
        ('less_than_15000', 'Less than P15,000'),
        ('15000_to_29999', 'P15,000 - P29,999'),
        ('30000_to_49999', 'P30,000 - P49,999'),
        ('50000_and_above', 'P50,000 and above'),
        ('prefer_not_to_say', 'Prefer not to say'),
    )
    RELEVANCE_CHOICES = (
        ('yes', 'Yes'),
        ('no', 'No'),
        ('somewhat', 'Somewhat'),
    )
    JOB_TYPE_CHOICES = (
        ('first_job', 'First Job'),
        ('current_job', 'Current Job'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='work_histories')
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    employment_status = models.CharField(max_length=50, choices=EMPLOYMENT_STATUS_CHOICES)
    classification = models.CharField(max_length=50, choices=CLASSIFICATION_CHOICES)
    occupation = models.CharField(max_length=255)
    employing_agency = models.CharField(max_length=255)
    how_got_job = models.CharField(max_length=100)
    monthly_income = models.CharField(max_length=50, choices=INCOME_CHOICES)
    is_breadwinner = models.BooleanField()
    length_of_service = models.CharField(max_length=50)
    college_education_relevant = models.CharField(max_length=10, choices=RELEVANCE_CHOICES)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    skills = models.ManyToManyField(Skill, related_name='work_histories', blank=True)

    def __str__(self):
        return f"{self.occupation} at {self.employing_agency} ({self.job_type})"