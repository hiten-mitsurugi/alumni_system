from django.db import models
from .custom_user import CustomUser


class Achievement(models.Model):
    """Model for user achievements and accomplishments"""
    ACHIEVEMENT_TYPES = [
        ('academic', 'Academic'),
        ('professional', 'Professional'),
        ('certification', 'Certification'),
        ('award', 'Award'),
        ('volunteer', 'Volunteer Work'),
        ('project', 'Project'),
        ('publication', 'Publication'),
        ('patent', 'Patent'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(CustomUser, related_name='achievements', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES)
    description = models.TextField(blank=True, null=True)
    organization = models.CharField(max_length=200, blank=True, null=True)
    date_achieved = models.DateField(null=True, blank=True)
    url = models.URLField(blank=True, null=True)  # Link to certificate, publication, etc.
    attachment = models.FileField(upload_to='achievements/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)  # Show prominently on profile
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_achieved', '-created_at']
        indexes = [
            models.Index(fields=['user', 'type']),
            models.Index(fields=['is_featured']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"