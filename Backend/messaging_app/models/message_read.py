import uuid
from django.db import models
from django.conf import settings


class MessageRead(models.Model):
    """Track which users have read which messages (for group messages)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(
        'Message',
        on_delete=models.CASCADE,
        related_name='read_by'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='read_messages'
    )
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['message', 'user']  # Prevent duplicate read records
        app_label = 'messaging_app'

    def __str__(self):
        return f"{self.user.username} read message {self.message.id}"
