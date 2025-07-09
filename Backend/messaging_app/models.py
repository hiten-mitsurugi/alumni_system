from django.db import models
from django.contrib.auth import get_user_model
from django_cryptography.fields import encrypt

User = get_user_model()

class GroupChat(models.Model):
    name = models.CharField(max_length=255)
    members = models.ManyToManyField(User, related_name='group_chats')
    admins = models.ManyToManyField(User, related_name='admin_group_chats')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', null=True, blank=True)
    group = models.ForeignKey(GroupChat, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    content = encrypt(models.TextField())
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver or self.group}"

class Reaction(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_reactions')  # Added related_name
    reaction_type = models.CharField(max_length=50)

    class Meta:
        unique_together = ('message', 'user', 'reaction_type')

class Attachment(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='attachments/')
    file_type = models.CharField(max_length=50)