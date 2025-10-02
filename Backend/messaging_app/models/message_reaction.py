import uuid
from django.db import models
from django.conf import settings


class MessageReaction(models.Model):
    """Enhanced for Facebook-style reactions"""
    REACTION_CHOICES = [
        ('like', '👍'),      # Approve/Like
        ('heart', '❤️'),     # Love/Heart
        ('haha', '😂'),      # Haha/Laugh
        ('sad', '😢'),       # Sad
        ('angry', '😠'),     # Angry
        ('care', '🤗'),      # Care/Hug
        ('dislike', '👎'),   # Disapprove/Dislike
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='message_reactions'
    )
    message = models.ForeignKey(
        'Message',
        on_delete=models.CASCADE,
        related_name='reactions'
    )
    reaction_type = models.CharField(max_length=10, choices=REACTION_CHOICES)
    emoji = models.CharField(max_length=10)  # Store the actual emoji
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'messaging_app'
        unique_together = ('user', 'message')  # One reaction per user per message
        indexes = [
            models.Index(fields=['message', 'reaction_type']),
            models.Index(fields=['user', 'message']),
        ]

    def save(self, *args, **kwargs):
        # Auto-set emoji based on reaction_type
        if self.reaction_type and not self.emoji:
            self.emoji = dict(self.REACTION_CHOICES).get(self.reaction_type, '👍')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} reacted {self.emoji} to message {self.message.id}"
