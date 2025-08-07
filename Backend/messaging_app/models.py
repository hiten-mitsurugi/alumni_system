import uuid
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_cryptography.fields import encrypt

# # --- UserProfile ---
# class UserProfile(models.Model):
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name='profile'
#     )
#     profile_picture = models.URLField(blank=True, null=True)
#     status = models.CharField(
#         max_length=20,
#         choices=[('online', 'Online'), ('offline', 'Offline')],
#         default='offline'
#     )
#     bio = models.TextField(blank=True, null=True)
#     last_seen = models.DateTimeField(null=True, blank=True)

# # Automatically create a UserProfile when a new user is created
# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created and not hasattr(instance, 'messaging_profile'):
#         UserProfile.objects.create(user=instance)

# --- Message ---
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

    class Meta:
        app_label = 'messaging_app'

# --- Attachment ---
class Attachment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to='attachments/')  # Like profile_picture field
    file_type = models.CharField(max_length=100, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'messaging_app'

# --- GroupChat ---
class GroupChat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    group_picture = models.URLField(blank=True, null=True)
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

    class Meta:
        app_label = 'messaging_app'

# --- MessageRequest ---
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

# --- BlockedUser ---
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

# --- MutedConversation ---
class MutedConversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='muted_by_user',
        on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='muted_conversations',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    group = models.ForeignKey(
        GroupChat,
        related_name='muted_groups',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    muted_until = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'messaging_app'

# --- Reaction ---
class Reaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reactions'
    )
    message = models.ForeignKey(
        'Message',
        on_delete=models.CASCADE,
        related_name='reactions'
    )
    emoji = models.CharField(max_length=10)  # example: "❤️", "😂", "👍"
    reacted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'messaging_app'
        unique_together = ('user', 'message', 'emoji')  # Prevent duplicate reactions
