import uuid
from django.db import models


class Attachment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to='attachments/')  # Like profile_picture field
    file_name = models.CharField(max_length=255, blank=True)  # Original filename
    file_type = models.CharField(max_length=100, blank=True)  # MIME type
    file_size = models.BigIntegerField(default=0)  # File size in bytes
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.file:
            # Auto-populate file metadata
            if not self.file_name and hasattr(self.file, 'name'):
                self.file_name = self.file.name
            if not self.file_size and hasattr(self.file, 'size'):
                self.file_size = self.file.size
            # Auto-detect MIME type if not provided
            if not self.file_type:
                import mimetypes
                mime_type, _ = mimetypes.guess_type(self.file.name)
                self.file_type = mime_type or 'application/octet-stream'
        super().save(*args, **kwargs)

    class Meta:
        app_label = 'messaging_app'
