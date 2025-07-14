from django.db import models
from django.contrib.auth import get_user_model
from django_cryptography.fields import encrypt
import uuid

User = get_user_model()

class UserProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='messaging_profile')
    status = models.CharField(max_length=20, choices=(('online', 'Online'), ('offline', 'Offline')), default='offline')
    last_seen = models.DateTimeField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)

    def __str__(self):
        return f"Profile for {self.user.username}"

class GroupChat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    members = models.ManyToManyField(User, related_name='group_chats')
    admins = models.ManyToManyField(User, related_name='admin_group_chats')
    created_at = models.DateTimeField(auto_now_add=True)
    group_picture = models.ImageField(upload_to='group_pictures/', null=True, blank=True)

    def __str__(self):
        return self.name

class MessageRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests')
    timestamp = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"Request from {self.sender} to {self.receiver}"

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', null=True, blank=True)
    group = models.ForeignKey('GroupChat', on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    content = encrypt(models.TextField())
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    reply_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='replies')

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver or self.group}"

class Reaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey('Message', on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_reactions')
    reaction_type = models.CharField(max_length=50)

    class Meta:
        unique_together = ('message', 'user', 'reaction_type')

    def __str__(self):
        return f"{self.reaction_type} by {self.user} on message {self.message.id}"

class Attachment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey('Message', on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='attachments/')
    file_type = models.CharField(max_length=50)

    def __str__(self):
        return f"Attachment for message {self.message.id}"

class BlockedUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_by')
    blocked_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_users')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'blocked_user')

    def __str__(self):
        return f"{self.user} blocked {self.blocked_user}"

class MutedConversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='muted_conversations')
    group = models.ForeignKey('GroupChat', null=True, blank=True, on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    muted_until = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Muted conversation for {self.user}"