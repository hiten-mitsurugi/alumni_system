"""
Profile, Social, Achievement, and Education Models
"""
from .base_models import *
from .user_models import CustomUser
from .skills_work_models import WorkHistory

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    timestamp = models.DateTimeField(auto_now_add=True)
    full_name = models.CharField(max_length=450, blank=True, null=True)
    email_address = models.EmailField(blank=True, null=True)
    mobile_number = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=20, choices=CustomUser.GENDER_CHOICES, blank=True, null=True)
    civil_status = models.CharField(max_length=20, choices=CustomUser.CIVIL_STATUS_CHOICES, blank=True, null=True)
    year_of_birth = models.DateField(blank=True, null=True)
    
    # Address fields have been normalized into the `Address` model.
    # Do not duplicate address columns here; use user.normalized_addresses instead.
    
    mothers_name = models.CharField(max_length=150, blank=True, null=True)
    mothers_occupation = models.CharField(max_length=100, blank=True, null=True)
    fathers_name = models.CharField(max_length=150, blank=True, null=True)
    fathers_occupation = models.CharField(max_length=100, blank=True, null=True)
    year_graduated = models.PositiveIntegerField(blank=True, null=True)
    program = models.CharField(max_length=100, blank=True, null=True)
    present_employment_status = models.CharField(max_length=50, choices=CustomUser.EMPLOYMENT_STATUS_CHOICES, blank=True, null=True)
    employment_classification = models.CharField(max_length=50, choices=WorkHistory.CLASSIFICATION_CHOICES, blank=True)
    present_occupation = models.CharField(max_length=255, blank=True)
    employing_agency = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=[('online', 'Online'), ('offline', 'Offline')], default='offline')
    bio = models.TextField(blank=True, null=True)
    last_seen = models.DateTimeField(null=True, blank=True)
    
    # LinkedIn-style additions
    cover_photo = models.ImageField(upload_to='cover_photos/', null=True, blank=True)
    headline = models.CharField(max_length=200, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    
    # Social media links
    linkedin_url = models.URLField(blank=True, null=True)
    facebook_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    
    # Privacy settings
    profile_visibility = models.CharField(
        max_length=20, 
        choices=[
            ('public', 'Public'),
            ('connections_only', 'Connections Only'),
            ('private', 'Private')
        ],
        default='public'
    )
    allow_contact = models.BooleanField(default=True)
    allow_messaging = models.BooleanField(default=True)
    
    def get_connections_count(self):
        """Get total connections count - unique people connected to this user"""
        # Get all unique user IDs that are connected to this user (either direction)
        # with accepted status, but count each person only once
        connected_user_ids = set()
        
        # Add users who follow this user (accepted)
        followers = Following.objects.filter(
            following=self.user, 
            status='accepted'
        ).values_list('follower_id', flat=True)
        connected_user_ids.update(followers)
        
        # Add users this user follows (accepted)  
        following = Following.objects.filter(
            follower=self.user, 
            status='accepted'
        ).values_list('following_id', flat=True)
        connected_user_ids.update(following)
        
        return len(connected_user_ids)
    
    def get_followers_count(self):
        """Get followers count"""
        return Following.objects.filter(following=self.user, status='accepted').count()
    
    def get_following_count(self):
        """Get following count"""
        return Following.objects.filter(follower=self.user, status='accepted').count()
    
    def get_posts_count(self):
        """Get user's posts count"""
        try:
            # Import here to avoid circular imports
            from posts_app.models import Post
            return Post.objects.filter(user=self.user).count()
        except ImportError:
            # If posts app is not available, return 0
            return 0

    def save(self, *args, **kwargs):
        self.full_name = f"{self.user.first_name} {self.user.middle_name or ''} {self.user.last_name}".strip()
        self.email_address = self.user.email
        self.mobile_number = self.user.contact_number
        self.sex = self.user.sex
        self.civil_status = self.user.civil_status
        self.year_of_birth = self.user.birth_date
        
        # Addresses are stored on the Address model; no field syncing here.
        
        self.mothers_name = self.user.mothers_name
        self.mothers_occupation = self.user.mothers_occupation
        self.fathers_name = self.user.fathers_name
        self.fathers_occupation = self.user.fathers_occupation
        self.year_graduated = self.user.year_graduated
        self.program = self.user.program
        
        # Only sync work history for alumni (user_type=3), not for admins (user_type=1,2)
        # NOTE: is_current_job field doesn't exist in database (migration mismatch)
        # So we skip syncing work history during profile creation, can be added later
        if self.user.user_type == 3:
            # Work histories are optional - skip syncing if not provided
            # (Can be added/updated through ExperienceModal after registration)
            pass
        
        super().save(*args, **kwargs)


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
        
        # Check if this is an update to an existing record
        is_update = self.pk is not None
        
        super().save(*args, **kwargs)
        
        # Only update mutual status for accepted connections on status change
        # Avoid recursive calls by checking if we're only updating is_mutual
        update_fields = kwargs.get('update_fields', None)
        if (self.status == 'accepted' and 
            is_update and 
            (update_fields is None or 'is_mutual' not in update_fields)):
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


class Achievement(models.Model):
    """Model for user achievements and accomplishments"""
    ACHIEVEMENT_TYPES = [
        ('academic', 'Academic'),
        ('professional', 'Professional'),
        ('certification', 'Certification'),
        ('award', 'Award'),
        ('volunteer', 'Volunteer Work'),
        ('project', 'Project'),
        ('publication', 'Publication'),
        ('patent', 'Patent'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(CustomUser, related_name='achievements', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES)
    description = models.TextField(blank=True, null=True)
    organization = models.CharField(max_length=200, blank=True, null=True)
    date_achieved = models.DateField(null=True, blank=True)
    url = models.URLField(blank=True, null=True)  # Link to certificate, publication, etc.
    attachment = models.FileField(upload_to='achievements/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)  # Show prominently on profile
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_achieved', '-created_at']
        indexes = [
            models.Index(fields=['user', 'type']),
            models.Index(fields=['is_featured']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"


class Education(models.Model):
    """Model for educational background"""
    DEGREE_TYPES = [
        ('high_school', 'High School'),
        ('vocational', 'Vocational'),
        ('associate', 'Associate Degree'),
        ('bachelor', 'Bachelor\'s Degree'),
        ('master', 'Master\'s Degree'),
        ('doctoral', 'Doctoral Degree'),
        ('certificate', 'Certificate'),
        ('diploma', 'Diploma'),
        ('other', 'Other'),
    ]
    
    REASON_CHOICES = [
        ('career_growth', 'Career growth'),
        ('interest', 'Interest'),
        ('job_requirement', 'Job requirement'),
        ('promotion', 'Promotion'),
        ('personal_development', 'Personal development'),
        ('others', 'Others'),
    ]
    
    user = models.ForeignKey(CustomUser, related_name='education', on_delete=models.CASCADE)
    institution = models.CharField(max_length=200)
    degree_type = models.CharField(max_length=20, choices=DEGREE_TYPES)
    field_of_study = models.CharField(max_length=200, blank=True, null=True)
    specialization = models.CharField(max_length=200, blank=True, null=True)
    is_related_to_undergrad = models.BooleanField(default=False)
    reason_for_further_study = models.JSONField(default=list, blank=True)  # Stores array of selected reasons
    reason_other_specify = models.TextField(blank=True, null=True)  # Text when "Others" is selected
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    gpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True, null=True)  # Activities, honors, etc.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-end_date', '-start_date']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['is_current']),
        ]
    
    def __str__(self):
        return f"{self.degree_type} at {self.institution} - {self.user.username}"
