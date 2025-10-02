from django.db import models
from .post import Post


class PostMedia(models.Model):
    """Support for multiple media files per post"""
    MEDIA_TYPES = (
        ('image', 'Image'),
        ('video', 'Video'),
        ('document', 'Document'),
    )
    
    post = models.ForeignKey(Post, related_name='media_files', on_delete=models.CASCADE)
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPES)
    file = models.FileField(upload_to='post_media/')
    thumbnail = models.ImageField(upload_to='post_thumbnails/', blank=True, null=True)
    caption = models.CharField(max_length=500, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'created_at']