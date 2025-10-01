from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        (1, 'Super Admin'),
        (2, 'Admin'),
        (3, 'Alumni'),
    )
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('prefer_not_to_say', 'Prefer not to say'),
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
    sex = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True, null=True)
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
    
    # Legacy address fields (keep for backward compatibility)
    present_address = models.TextField(blank=True, null=True)
    permanent_address = models.TextField(blank=True, null=True)
    
    # Present Address - Structured Fields
    present_address_type = models.CharField(max_length=20, choices=[('philippines', 'Philippines'), ('international', 'International')], default='philippines', blank=True)
    present_region_code = models.CharField(max_length=10, blank=True, null=True)
    present_region_name = models.CharField(max_length=100, blank=True, null=True)
    present_province_code = models.CharField(max_length=10, blank=True, null=True)
    present_province_name = models.CharField(max_length=100, blank=True, null=True)
    present_city_code = models.CharField(max_length=10, blank=True, null=True)
    present_city_name = models.CharField(max_length=100, blank=True, null=True)
    present_barangay = models.CharField(max_length=100, blank=True, null=True)
    present_street_address = models.CharField(max_length=255, blank=True, null=True)
    present_postal_code = models.CharField(max_length=10, blank=True, null=True)
    present_country = models.CharField(max_length=100, blank=True, null=True)
    present_full_address = models.TextField(blank=True, null=True)
    
    # Permanent Address - Structured Fields
    permanent_address_type = models.CharField(max_length=20, choices=[('philippines', 'Philippines'), ('international', 'International')], default='philippines', blank=True)
    permanent_region_code = models.CharField(max_length=10, blank=True, null=True)
    permanent_region_name = models.CharField(max_length=100, blank=True, null=True)
    permanent_province_code = models.CharField(max_length=10, blank=True, null=True)
    permanent_province_name = models.CharField(max_length=100, blank=True, null=True)
    permanent_city_code = models.CharField(max_length=10, blank=True, null=True)
    permanent_city_name = models.CharField(max_length=100, blank=True, null=True)
    permanent_barangay = models.CharField(max_length=100, blank=True, null=True)
    permanent_street_address = models.CharField(max_length=255, blank=True, null=True)
    permanent_postal_code = models.CharField(max_length=10, blank=True, null=True)
    permanent_country = models.CharField(max_length=100, blank=True, null=True)
    permanent_full_address = models.TextField(blank=True, null=True)
    
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
        """Get formatted present address for display"""
        if self.present_address_type == 'philippines':
            parts = []
            if self.present_street_address:
                parts.append(self.present_street_address)
            if self.present_barangay:
                parts.append(f"Brgy. {self.present_barangay}")
            if self.present_city_name:
                parts.append(self.present_city_name)
            if self.present_province_name:
                parts.append(self.present_province_name)
            if self.present_region_name:
                parts.append(self.present_region_name)
            if self.present_postal_code:
                parts.append(self.present_postal_code)
            return ", ".join(parts) if parts else self.present_address or ''
        elif self.present_address_type == 'international':
            if self.present_full_address and self.present_country:
                return f"{self.present_full_address}, {self.present_country}"
            return self.present_address or ''
        return self.present_address or ''
    
    def get_formatted_permanent_address(self):
        """Get formatted permanent address for display"""
        if self.permanent_address_type == 'philippines':
            parts = []
            if self.permanent_street_address:
                parts.append(self.permanent_street_address)
            if self.permanent_barangay:
                parts.append(f"Brgy. {self.permanent_barangay}")
            if self.permanent_city_name:
                parts.append(self.permanent_city_name)
            if self.permanent_province_name:
                parts.append(self.permanent_province_name)
            if self.permanent_region_name:
                parts.append(self.permanent_region_name)
            if self.permanent_postal_code:
                parts.append(self.permanent_postal_code)
            return ", ".join(parts) if parts else self.permanent_address or ''
        elif self.permanent_address_type == 'international':
            if self.permanent_full_address and self.permanent_country:
                return f"{self.permanent_full_address}, {self.permanent_country}"
            return self.permanent_address or ''
        return self.permanent_address or ''