import uuid
from django.db import models
from django.conf import settings


class GroupChat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    group_picture = models.ImageField(
        upload_to='group_pictures/', 
        blank=True, 
        null=True,
        help_text="Group profile picture"
    )
    description = models.TextField(max_length=500, blank=True, null=True)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='group_chats'
    )
    admins = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='admin_groups',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'messaging_app'
        
    def __str__(self):
        return f"Group: {self.name} ({self.members.count()} members)"
