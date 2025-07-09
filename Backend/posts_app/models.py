from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from auth_app.models import CustomUser

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
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    content_category = models.CharField(max_length=20, choices=CONTENT_CATEGORIES)
    category = models.ForeignKey(PostCategory, on_delete=models.SET_NULL, null=True)
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Comment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', related_name='replies', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.email} on {self.post.title}"

class Reaction(models.Model):
    REACTION_TYPES = (
        ('like', 'Like'),
        ('heart', 'Heart'),
        ('dislike', 'Dislike'),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='post_reactions')  # Added related_name
    reaction_type = models.CharField(max_length=20, choices=REACTION_TYPES)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'content_type', 'object_id', 'reaction_type']

    def __str__(self):
        return f"{self.user.email} - {self.reaction_type}"