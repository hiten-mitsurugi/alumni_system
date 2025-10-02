from django.db import models
from auth_app.models import CustomUser
from .post_category import PostCategory


class Post(models.Model):
    CONTENT_CATEGORIES = (
        ('event', 'Event'),
        ('news', 'News'),
        ('discussion', 'Discussion'),
        ('announcement', 'Announcement'),
        ('job', 'Job'),
        ('others', 'Others'),
    )
    
    POST_TYPES = (
        ('original', 'Original Post'),
        ('shared', 'Shared Post'),
        ('repost', 'Repost'),
    )
    
    # Keep existing ID structure to avoid migration issues
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=200, blank=True)  # Optional for Facebook-style posts
    content = models.TextField()
    content_category = models.CharField(max_length=20, choices=CONTENT_CATEGORIES)
    category = models.ForeignKey(PostCategory, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Facebook-like features
    post_type = models.CharField(max_length=20, choices=POST_TYPES, default='original')
    shared_post = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='shares')
    shared_text = models.TextField(blank=True)  # Text when sharing a post
    
    # Media support
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    
    # Engagement metrics
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    shares_count = models.PositiveIntegerField(default=0)
    
    # Status and permissions
    is_approved = models.BooleanField(default=True)  # Auto-approve all posts
    is_pinned = models.BooleanField(default=False)
    visibility = models.CharField(max_length=20, choices=[
        ('public', 'Public'),
        ('alumni_only', 'Alumni Only'),
        ('admin_only', 'Admin Only')
    ], default='public')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    edited_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.first_name}'s post - {self.content[:50]}..."

    def auto_approve_if_admin(self):
        """Auto-approve posts from admin/superadmin users"""
        if self.user.user_type in [1, 2]:  # Admin or SuperAdmin
            self.is_approved = True