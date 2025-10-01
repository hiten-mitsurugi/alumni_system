from django.db import models
from django.conf import settings


class AlumniDirectory(models.Model):
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('prefer_not_to_say', 'Prefer not to say'),
    )
    
    first_name = models.CharField(max_length=150)
    middle_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150)
    birth_date = models.DateField()
    program = models.CharField(max_length=100)
    year_graduated = models.PositiveIntegerField()
    sex = models.CharField(max_length=20, choices=GENDER_CHOICES)

    class Meta:
        indexes = [
            models.Index(fields=['first_name', 'last_name', 'birth_date', 'program', 'year_graduated']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.program} - {self.year_graduated})"