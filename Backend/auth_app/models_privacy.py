from django.db import models
from .models import CustomUser

class FieldPrivacySetting(models.Model):
    """Model to handle per-field privacy settings for user profiles"""
    VISIBILITY_CHOICES = [
        ('public', 'For Everyone'),
        ('connections_only', 'For Connections'),
        ('private', 'Only for Me'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='field_privacy_settings')
    field_name = models.CharField(max_length=100)  # e.g., 'first_name', 'email', 'contact_number'
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='alumni_only')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'field_name')
        indexes = [
            models.Index(fields=['user', 'field_name']),
            models.Index(fields=['visibility']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.field_name}: {self.visibility}"

    @classmethod
    def get_user_field_visibility(cls, user, field_name):
        """Get visibility setting for a specific field"""
        try:
            setting = cls.objects.get(user=user, field_name=field_name)
            return setting.visibility
        except cls.DoesNotExist:
            return 'connections_only'  # Default visibility
    
    @classmethod
    def set_user_field_visibility(cls, user, field_name, visibility):
        """Set visibility for a specific field"""
        setting, created = cls.objects.get_or_create(
            user=user,
            field_name=field_name,
            defaults={'visibility': visibility}
        )
        if not created:
            setting.visibility = visibility
            setting.save()
        return setting