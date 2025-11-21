from django.db import models
from django.conf import settings
from django.utils import timezone


class Notification(models.Model):
    """
    Stores notifications for alumni users.
    Types: connection, survey, profile, post, system
    (message type excluded - handled by messaging_app)
    """
    
    TYPE_CHOICES = [
        ('connection', 'Connection'),
        ('survey', 'Survey'),
        ('profile', 'Profile'),
        ('post', 'Post'),
        ('system', 'System'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        db_index=True
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='notifications_triggered',
        null=True,
        blank=True,
        help_text='User who triggered this notification'
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, db_index=True)
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    # Navigation target
    link_route = models.CharField(max_length=255, blank=True, null=True)
    link_params = models.JSONField(default=dict, blank=True)
    
    # Additional data (e.g., post_id, comment_id, survey_id)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True, db_index=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'read_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.type} - {self.title}"
    
    @property
    def is_read(self):
        return self.read_at is not None
    
    def mark_as_read(self):
        if not self.read_at:
            self.read_at = timezone.now()
            self.save(update_fields=['read_at'])

