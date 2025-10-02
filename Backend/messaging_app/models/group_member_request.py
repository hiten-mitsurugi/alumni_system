import uuid
from django.db import models
from django.conf import settings


class GroupMemberRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(
        'GroupChat',
        on_delete=models.CASCADE,
        related_name='member_requests'
    )
    requested_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='group_requests_received'
    )
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='group_requests_made'
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected')
        ],
        default='pending'
    )
    message = models.TextField(blank=True, null=True, help_text="Optional message from requester")
    admin_response = models.TextField(blank=True, null=True, help_text="Optional response from admin")
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='group_requests_reviewed'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['group', 'requested_user']  # Prevent duplicate requests
        app_label = 'messaging_app'

    def __str__(self):
        return f"{self.requester.username} requested {self.requested_user.username} for {self.group.name}"
