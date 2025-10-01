from django.db import models
from django.contrib.auth import get_user_model
from .custom_user import CustomUser
from .work_history import WorkHistory


class Profile(models.Model):
    """Extended profile information for users"""
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    
    # Basic profile info
    bio = models.TextField(max_length=500, blank=True, default="")
    location = models.CharField(max_length=100, blank=True, default="")
    website = models.URLField(blank=True, default="")
    birth_date = models.DateField(null=True, blank=True)
    
    # Profile picture
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    cover_photo = models.ImageField(upload_to='cover_photos/', blank=True, null=True)
    
    # Privacy settings
    is_public = models.BooleanField(default=True)
    show_email = models.BooleanField(default=False)
    show_phone = models.BooleanField(default=False)
    
    # Social links
    linkedin_url = models.URLField(blank=True, default="")
    twitter_url = models.URLField(blank=True, default="")
    facebook_url = models.URLField(blank=True, default="")
    instagram_url = models.URLField(blank=True, default="")
    
    # Preferences  
    allow_contact = models.BooleanField(default=True)
    allow_messaging = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Employment status fields (derived from work history)
    present_employment_status = models.CharField(max_length=50, blank=True, null=True)
    employment_classification = models.CharField(max_length=50, blank=True, null=True)
    present_occupation = models.CharField(max_length=100, blank=True, null=True)
    employing_agency = models.CharField(max_length=200, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        # Auto-populate employment fields from most recent work history
        current_job = WorkHistory.objects.filter(
            user=self.user,
            job_type='current_job'
        ).first()
        
        if current_job:
            self.present_employment_status = current_job.employment_status
            self.employment_classification = current_job.classification
            self.present_occupation = current_job.occupation
            self.employing_agency = current_job.employing_agency
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_followers_count(self):
        """Get count of users following this profile's user"""
        from .following import Following
        return Following.objects.filter(following=self.user, status='accepted').count()
    
    def get_following_count(self):
        """Get count of users this profile's user is following"""
        from .following import Following
        return Following.objects.filter(follower=self.user, status='accepted').count()
    
    def get_connections_count(self):
        """Get count of mutual connections"""
        from .following import Following
        return Following.objects.filter(
            follower=self.user, 
            status='accepted',
            is_mutual=True
        ).count()