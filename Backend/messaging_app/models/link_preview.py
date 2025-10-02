import uuid
from django.db import models


class LinkPreview(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(
        'Message',
        on_delete=models.CASCADE,
        related_name='link_previews'
    )
    url = models.URLField(max_length=2048)
    title = models.CharField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image_url = models.URLField(max_length=2048, blank=True, null=True)
    domain = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'messaging_app'
