import uuid
from django.db import models
from django.conf import settings


class BlockedUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='blocked_users',
        on_delete=models.CASCADE
    )
    blocked_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='blocked_by',
        on_delete=models.CASCADE
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'messaging_app'
