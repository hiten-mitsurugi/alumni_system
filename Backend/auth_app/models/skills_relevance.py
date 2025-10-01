from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings


class SkillsRelevance(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='skills_relevance')
    critical_thinking = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    communication = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    innovation = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    collaboration = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    leadership = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    productivity_accountability = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    entrepreneurship = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    global_citizenship = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    adaptability = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    accessing_analyzing_synthesizing_info = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])