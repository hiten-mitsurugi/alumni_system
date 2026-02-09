"""
User and Address Models
"""
from .base_models import *
from django.utils.translation import gettext_lazy as _

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
        ('transgender', 'Transgender'),
        ('prefer_not_to_say', 'Prefer not to say'),
        ('other_specify', 'Other (please specify)'),
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
