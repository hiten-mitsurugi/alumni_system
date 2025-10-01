from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings


class CurriculumRelevance(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='curriculum_relevance')
    general_education = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    core_major = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    special_professional = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    electives = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    internship_ojt = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    co_curricular_activities = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    extra_curricular_activities = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])