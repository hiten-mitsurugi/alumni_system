from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from auth_app.models import CustomUser


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
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reactions')
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