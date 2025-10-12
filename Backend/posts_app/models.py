from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
import uuid

class PostCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
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
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived')
    ], default='published')  # Add this field to fix database constraint
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

class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', related_name='replies', on_delete=models.CASCADE, null=True, blank=True)
    
    # Engagement metrics
    likes_count = models.PositiveIntegerField(default=0)
    replies_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    edited_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.user.first_name} on {self.post.id}"

class Reaction(models.Model):
    """LinkedIn-style reactions for posts and comments"""
    REACTION_TYPES = (
        ('like', '👍'),
        ('applaud', '👏'),
        ('heart', '❤️'),
        ('support', '🤝'),
        ('laugh', '😂'),
        ('sad', '😢'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reactions')
    reaction_type = models.CharField(max_length=20, choices=REACTION_TYPES)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()  # Keep as integer for compatibility
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'content_type', 'object_id']

    def __str__(self):
        return f"{self.user.first_name} - {self.reaction_type}"

    @property
    def emoji(self):
        return dict(self.REACTION_TYPES)[self.reaction_type]

class PostView(models.Model):
    """Track post views for analytics"""
    post = models.ForeignKey(Post, related_name='views', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['post', 'user']  # One view per user per post

class PostReport(models.Model):
    """Allow users to report inappropriate posts"""
    REPORT_REASONS = (
        ('spam', 'Spam'),
        ('harassment', 'Harassment and Bullying'),
        ('inappropriate', 'Inappropriate Content'),
        ('false_information', 'False Information'),
        ('violence', 'Violence or Threats'),
        ('copyright', 'Copyright Infringement'),
        ('other', 'Other'),
    )
    
    post = models.ForeignKey(Post, related_name='reports', on_delete=models.CASCADE)
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reason = models.CharField(max_length=50, choices=REPORT_REASONS)
    description = models.TextField(blank=True)
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_reports')
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

class SavedPost(models.Model):
    """Allow users to save posts for later"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_posts')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='saved_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'post']
