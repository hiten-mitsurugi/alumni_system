import uuid
from django.db import models
from django.conf import settings
from django_cryptography.fields import encrypt


class MessageRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='sent_requests',
        on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='received_requests',
        on_delete=models.CASCADE
    )
    content = encrypt(models.TextField(blank=True, null=True))  # Encrypt message request content
    timestamp = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    class Meta:
        app_label = 'messaging_app'
