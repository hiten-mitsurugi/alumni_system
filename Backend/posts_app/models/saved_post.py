from django.db import models
from auth_app.models import CustomUser
from .post import Post


class SavedPost(models.Model):
    """Allow users to save posts for later"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='saved_posts')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='saved_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'post']