from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings


class PerceptionFurtherStudies(models.Model):
    MODE_OF_STUDY_CHOICES = (
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('online', 'Online'),
        ('others', 'Others'),
    )
    LEVEL_OF_STUDY_CHOICES = (
        ('masters', "Master's"),
        ('doctoral', 'Doctoral'),
        ('certificate', 'Certificate'),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='perception_studies')
    competitiveness = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    pursued_further_studies = models.BooleanField()
    mode_of_study = models.CharField(max_length=50, choices=MODE_OF_STUDY_CHOICES, blank=True, default="")
    level_of_study = models.CharField(max_length=50, choices=LEVEL_OF_STUDY_CHOICES, blank=True, default="")
    field_of_study = models.CharField(max_length=100, blank=True, default="")
    specialization = models.CharField(max_length=100, blank=True, default="")
    related_to_undergrad = models.BooleanField(null=True)
    reasons_for_further_study = models.TextField(blank=True, default="")