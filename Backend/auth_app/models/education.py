from django.db import models
from .custom_user import CustomUser


class Education(models.Model):
    """Model for educational background"""
    DEGREE_TYPES = [
        ('high_school', 'High School'),
        ('associate', 'Associate Degree'),
        ('bachelor', 'Bachelor\'s Degree'),
        ('master', 'Master\'s Degree'),
        ('doctoral', 'Doctoral Degree'),
        ('certificate', 'Certificate'),
        ('diploma', 'Diploma'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(CustomUser, related_name='education', on_delete=models.CASCADE)
    institution = models.CharField(max_length=200)
    degree_type = models.CharField(max_length=20, choices=DEGREE_TYPES)
    field_of_study = models.CharField(max_length=200, blank=True, null=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    gpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True, null=True)  # Activities, honors, etc.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-end_date', '-start_date']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['is_current']),
        ]
    
    def __str__(self):
        return f"{self.degree_type} at {self.institution} - {self.user.username}"