from django.db import models
from .custom_user import CustomUser


class Following(models.Model):
    """Model to handle following/connections between users (LinkedIn-style)"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('blocked', 'Blocked'),
    ]
    
    follower = models.ForeignKey(CustomUser, related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(CustomUser, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_mutual = models.BooleanField(default=False)  # True if both follow each other
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='accepted')  # New field
    
    class Meta:
        unique_together = ('follower', 'following')
        indexes = [
            models.Index(fields=['follower']),
            models.Index(fields=['following']),
            models.Index(fields=['is_mutual']),
            models.Index(fields=['status']),
        ]
    
    def save(self, *args, **kwargs):
        # Prevent self-following
        if self.follower == self.following:
            raise ValueError("Users cannot follow themselves")
        
        super().save(*args, **kwargs)
        
        # Only update mutual status for accepted connections
        if self.status == 'accepted':
            self.update_mutual_status()
    
    def update_mutual_status(self):
        """Update mutual following status for both users"""
        # Check if the reverse relationship exists and is accepted
        reverse_follow = Following.objects.filter(
            follower=self.following, 
            following=self.follower,
            status='accepted'
        ).first()
        
        if reverse_follow:
            # Both follow each other - mark as mutual
            self.is_mutual = True
            reverse_follow.is_mutual = True
            self.save(update_fields=['is_mutual'])
            reverse_follow.save(update_fields=['is_mutual'])
        else:
            # Not mutual
            self.is_mutual = False
            self.save(update_fields=['is_mutual'])
    
    def accept_invitation(self):
        """Accept a pending invitation and create mutual connection (LinkedIn-style)"""
        if self.status == 'pending':
            self.status = 'accepted'
            self.save()
            
            # Create reverse connection automatically for mutual relationship
            reverse_connection, created = Following.objects.get_or_create(
                follower=self.following,  # The person who accepted becomes follower
                following=self.follower,  # The person who sent request becomes following
                defaults={'status': 'accepted'}
            )
            
            # Mark both relationships as mutual
            self.is_mutual = True
            reverse_connection.is_mutual = True
            self.save(update_fields=['is_mutual'])
            reverse_connection.save(update_fields=['is_mutual'])
            
            return True
        return False
    
    def reject_invitation(self):
        """Reject a pending invitation"""
        if self.status == 'pending':
            self.delete()
            return True
        return False
    
    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"