from django.db import models
from auth_app.models import CustomUser
from .post import Post


class PostReport(models.Model):
    """Allow users to report inappropriate posts"""
    REPORT_REASONS = (
        ('spam', 'Spam'),
        ('harassment', 'Harassment'),
        ('inappropriate', 'Inappropriate Content'),
        ('fake_news', 'Fake News'),
        ('violence', 'Violence'),
        ('other', 'Other'),
    )
    
    post = models.ForeignKey(Post, related_name='reports', on_delete=models.CASCADE)
    reporter = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    reason = models.CharField(max_length=50, choices=REPORT_REASONS)
    description = models.TextField(blank=True)
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_reports')
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)