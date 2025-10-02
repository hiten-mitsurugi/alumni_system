import uuid
from django.db import models
from django.conf import settings


class MessageMention(models.Model):
    """Track user mentions in messages"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(
        'Message',
        on_delete=models.CASCADE,
        related_name='mentions'
    )
    mentioned_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='message_mentions'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['message', 'mentioned_user']  # Prevent duplicate mentions
        app_label = 'messaging_app'
        indexes = [
            models.Index(fields=['message', 'mentioned_user']),
            models.Index(fields=['mentioned_user', 'created_at']),
        ]

    def __str__(self):
        return f"{self.mentioned_user.username} mentioned in message {self.message.id}"
