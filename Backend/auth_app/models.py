from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        (1, 'Super Admin'),
        (2, 'Admin'),
        (3, 'Alumni'),
    )
    SEX_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
    )
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('non_binary', 'Non-binary'),
        ('prefer_not_to_say', 'Prefer not to say'),
        ('other', 'Other'),
    )
    CIVIL_STATUS_CHOICES = (
        ('single', 'Single'),
        ('married', 'Married'),
        ('separated', 'Separated'),
        ('widowed', 'Widowed'),
    )
    EMPLOYMENT_STATUS_CHOICES = (
        ('employed_locally', 'Employed Locally'),
        ('employed_internationally', 'Employed Internationally'),
        ('self_employed', 'Self-Employed'),
        ('unemployed', 'Unemployed'),
        ('retired', 'Retired'),
    )

    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, default=3)
    sex = models.CharField(max_length=20, choices=SEX_CHOICES, blank=True, null=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True, null=True)
    civil_status = models.CharField(max_length=20, choices=CIVIL_STATUS_CHOICES, blank=True, null=True)
    employment_status = models.CharField(max_length=100, choices=EMPLOYMENT_STATUS_CHOICES, blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    email = models.EmailField(_('email address'), unique=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    middle_name = models.CharField(max_length=150, blank=True, null=True)
    government_id = models.FileField(upload_to='government_ids/', null=True, blank=True)
    program = models.CharField(max_length=100, blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    year_graduated = models.PositiveIntegerField(blank=True, null=True)
    
    # Address data moved to `Address` model. Keep no legacy fields here.
    
    mothers_name = models.CharField(max_length=150, blank=True, null=True)
    mothers_occupation = models.CharField(max_length=100, blank=True, null=True)
    fathers_name = models.CharField(max_length=150, blank=True, null=True)
    fathers_occupation = models.CharField(max_length=100, blank=True, null=True)

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'password', 'program', 'birth_date', 'year_graduated']

    class Meta:
        indexes = [
            models.Index(fields=['user_type', 'is_approved']),
            models.Index(fields=['first_name', 'last_name', 'birth_date', 'program', 'year_graduated']),
        ]

    def __str__(self):
        return self.username
    def get_formatted_present_address(self):
        """Return formatted present address from the Address model if exists."""
        addr = self.normalized_addresses.filter(address_category='present').first()
        if addr:
            return addr.get_formatted_address()
        return ''

    def get_formatted_permanent_address(self):
        """Return formatted permanent address from the Address model if exists."""
        addr = self.normalized_addresses.filter(address_category='permanent').first()
        if addr:
            return addr.get_formatted_address()
        return ''


class Address(models.Model):
    """Normalized address model to store user addresses separately"""
    ADDRESS_CATEGORY_CHOICES = [
        ('present', 'Present'),
        ('permanent', 'Permanent'),
    ]
    ADDRESS_TYPE_CHOICES = [
        ('philippines', 'Philippines'),
        ('international', 'International'),
    ]

    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='normalized_addresses')
    address_category = models.CharField(max_length=20, choices=ADDRESS_CATEGORY_CHOICES)
    address_type = models.CharField(max_length=20, choices=ADDRESS_TYPE_CHOICES, default='philippines')
    
    # Philippines structured fields
    region_code = models.CharField(max_length=10, blank=True, null=True)
    region_name = models.CharField(max_length=100, blank=True, null=True)
    province_code = models.CharField(max_length=10, blank=True, null=True)
    province_name = models.CharField(max_length=100, blank=True, null=True)
    city_code = models.CharField(max_length=10, blank=True, null=True)
    city_name = models.CharField(max_length=100, blank=True, null=True)
    barangay = models.CharField(max_length=100, blank=True, null=True)
    street_address = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    
    # International fields
    country = models.CharField(max_length=100, blank=True, null=True)
    full_address = models.TextField(blank=True, null=True)
    
    # Computed field for deduplication and display
    normalized_text = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('user', 'address_category')]  # One present, one permanent per user
        indexes = [
            models.Index(fields=['user', 'address_category']),
            models.Index(fields=['address_type']),
            models.Index(fields=['city_name']),
            models.Index(fields=['postal_code']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.get_address_category_display()}"

    def get_formatted_address(self):
        """Get formatted address for display"""
        if self.address_type == 'philippines':
            # Try structured fields first
            parts = []
            if self.street_address:
                parts.append(self.street_address)
            if self.barangay:
                parts.append(f"Brgy. {self.barangay}")
            if self.city_name:
                parts.append(self.city_name)
            if self.province_name:
                parts.append(self.province_name)
            if self.region_name:
                parts.append(self.region_name)
            if self.postal_code:
                parts.append(self.postal_code)
            
            # If structured fields exist, use them
            if parts:
                return ", ".join(parts)
            # Otherwise, fall back to full_address for simple address updates
            elif self.full_address:
                return self.full_address
            else:
                return ""
        elif self.address_type == 'international':
            if self.full_address and self.country:
                return f"{self.full_address}, {self.country}"
            return self.full_address or ""
        return ""

    def save(self, *args, **kwargs):
        """Auto-populate normalized_text on save"""
        self.normalized_text = self.get_formatted_address()
        super().save(*args, **kwargs)


class AlumniDirectory(models.Model):
    first_name = models.CharField(max_length=150)
    middle_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150)
    birth_date = models.DateField()
    program = models.CharField(max_length=100)
    year_graduated = models.PositiveIntegerField()
    sex = models.CharField(max_length=20, choices=CustomUser.SEX_CHOICES)

    class Meta:
        indexes = [
            models.Index(fields=['first_name', 'last_name', 'birth_date', 'program', 'year_graduated']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.program} - {self.year_graduated})"

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    def __str__(self):
        return self.name

class UserSkill(models.Model):
    CATEGORY_CHOICES = (
        ('technical', 'Technical'),
        ('soft_skills', 'Soft Skills'),
        ('languages', 'Languages'),
        ('tools', 'Tools & Software'),
        ('other', 'Other'),
    )
    
    PROFICIENCY_CHOICES = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_skills')
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    proficiency = models.CharField(max_length=20, choices=PROFICIENCY_CHOICES, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'name', 'category']
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.category}) - {self.user.username}"

class WorkHistory(models.Model):
    CLASSIFICATION_CHOICES = (
        ('government', 'Government'),
        ('private', 'Private'),
        ('ngo', 'NGO'),
        ('freelance', 'Freelance'),
        ('business_owner', 'Business Owner'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='work_histories')
    # Core fields
    occupation = models.CharField(max_length=255)
    employing_agency = models.CharField(max_length=255)
    classification = models.CharField(max_length=50, choices=CLASSIFICATION_CHOICES)
    length_of_service = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_current_job = models.BooleanField(default=False)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    skills = models.ManyToManyField(Skill, related_name='work_histories', blank=True)

    def __str__(self):
        current_status = "Current" if self.is_current_job else "Previous"
        return f"{self.occupation} at {self.employing_agency} ({current_status})"

class SkillsRelevance(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='skills_relevance')
    critical_thinking = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    communication = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    innovation = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    collaboration = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    leadership = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    productivity_accountability = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    entrepreneurship = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    global_citizenship = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    adaptability = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    accessing_analyzing_synthesizing_info = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

class CurriculumRelevance(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='curriculum_relevance')
    general_education = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    core_major = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    special_professional = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    electives = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    internship_ojt = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    co_curricular_activities = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    extra_curricular_activities = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

class PerceptionFurtherStudies(models.Model):
    MODE_OF_STUDY_CHOICES = (
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('online', 'Online'),
        ('others', 'Others'),
    )
    LEVEL_OF_STUDY_CHOICES = (
        ('masters', "Master's"),
        ('doctoral', 'Doctoral'),
        ('certificate', 'Certificate'),
    )

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='perception_studies')
    competitiveness = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    pursued_further_studies = models.BooleanField()
    mode_of_study = models.CharField(max_length=50, choices=MODE_OF_STUDY_CHOICES, blank=True)
    level_of_study = models.CharField(max_length=50, choices=LEVEL_OF_STUDY_CHOICES, blank=True)
    field_of_study = models.CharField(max_length=100, blank=True)
    specialization = models.CharField(max_length=100, blank=True)
    related_to_undergrad = models.BooleanField(null=True)
    reasons_for_further_study = models.TextField(blank=True)

class FeedbackRecommendations(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='feedback')
    recommendations = models.TextField(blank=True)

# auth_app/models.py (only the Profile model is shown for brevity)
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
            ('public', 'For Everyone'),
            ('connections_only', 'For Connections'),
            ('private', 'Only for Me')
        ],
        default='connections_only'
    )
    allow_contact = models.BooleanField(default=True)
    allow_messaging = models.BooleanField(default=True)
    
    def get_connections_count(self):
        """Get total connections count"""
        return Following.objects.filter(
            models.Q(follower=self.user) | models.Q(following=self.user),
            is_mutual=True
        ).count() // 2  # Divide by 2 since mutual connections appear twice
    
    def get_followers_count(self):
        """Get followers count"""
        return Following.objects.filter(following=self.user).count()
    
    def get_following_count(self):
        """Get following count"""
        return Following.objects.filter(follower=self.user).count()

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
        if self.user.user_type == 3:
            current_job = self.user.work_histories.filter(is_current_job=True).first()
            if current_job:
                # Map to existing profile fields for compatibility
                self.present_employment_status = current_job.classification  # Use classification instead of removed employment_status
                self.employment_classification = current_job.classification
                self.present_occupation = current_job.occupation
                self.employing_agency = current_job.employing_agency
        
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
    
    user = models.ForeignKey(CustomUser, related_name='education', on_delete=models.CASCADE)
    institution = models.CharField(max_length=200)
    degree_type = models.CharField(max_length=20, choices=DEGREE_TYPES)
    field_of_study = models.CharField(max_length=200, blank=True, null=True)
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


class FieldPrivacySetting(models.Model):
    """Model to handle per-field privacy settings for user profiles"""
    VISIBILITY_CHOICES = [
        ('everyone', 'For Everyone'),
        ('connections_only', 'For Connections'),
        ('only_me', 'Only for Me'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='field_privacy_settings')
    field_name = models.CharField(max_length=100)  # e.g., 'first_name', 'email', 'contact_number'
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='connections_only')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'field_name')
        indexes = [
            models.Index(fields=['user', 'field_name']),
            models.Index(fields=['visibility']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.field_name}: {self.visibility}"

    @classmethod
    def get_user_field_visibility(cls, user, field_name):
        """Get visibility setting for a specific field"""
        try:
            setting = cls.objects.get(user=user, field_name=field_name)
            return setting.visibility
        except cls.DoesNotExist:
            return 'connections_only'  # Default visibility
    
    @classmethod
    def set_user_field_visibility(cls, user, field_name, visibility):
        """Set visibility for a specific field"""
        setting, created = cls.objects.get_or_create(
            user=user,
            field_name=field_name,
            defaults={'visibility': visibility}
        )
        if not created:
            setting.visibility = visibility
            setting.save()
        return setting


class SectionPrivacySetting(models.Model):
    pass

