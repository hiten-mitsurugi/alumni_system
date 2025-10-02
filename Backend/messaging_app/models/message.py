import uuid
from django.db import models
from django.conf import settings
from django_cryptography.fields import encrypt


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='sent_messages',
        on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='received_messages',
        on_delete=models.CASCADE,
        null=True
    )
    group = models.ForeignKey('GroupChat', on_delete=models.CASCADE, null=True)
    content = encrypt(models.TextField())  # Encrypt message content
    timestamp = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(null=True, blank=True)  # Track when message was last edited
    is_read = models.BooleanField(default=False)
    attachments = models.ManyToManyField('Attachment', blank=True)
    is_pinned = models.BooleanField(default=False)
    reply_to = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    # Forwarding fields
    forwarded_from = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='forwarded_messages',
        help_text='Original message that was forwarded'
    )
    is_forwarded = models.BooleanField(default=False, help_text='Whether this message is a forwarded message')

    class Meta:
        app_label = 'messaging_app'
