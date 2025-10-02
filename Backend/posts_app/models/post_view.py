from django.db import models
from auth_app.models import CustomUser
from .post import Post


class PostView(models.Model):
    """Track post views for analytics"""
    post = models.ForeignKey(Post, related_name='views', on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['post', 'user']  # One view per user per post