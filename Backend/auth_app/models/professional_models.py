"""
Professional Development Models - Memberships, Recognitions, Trainings, Publications, Certificates, CSE Status
"""
from .base_models import *
from .user_models import CustomUser

class Membership(models.Model):
    """Model for storing user organization memberships"""
    MEMBERSHIP_TYPE_CHOICES = [
        ('active', 'Active Member'),
        ('inactive', 'Inactive Member'),
        ('honorary', 'Honorary Member'),
        ('lifetime', 'Lifetime Member'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='memberships')
    organization_name = models.CharField(max_length=255)
    position = models.CharField(max_length=120, blank=True, null=True)
    membership_type = models.CharField(max_length=20, choices=MEMBERSHIP_TYPE_CHOICES, default='active')
    date_joined = models.DateField(blank=True, null=True)
    date_ended = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_joined', '-created_at']
        indexes = [
            models.Index(fields=['user', 'membership_type']),
            models.Index(fields=['organization_name']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.organization_name}"
    
    @property
    def is_current(self):
        """Check if membership is still active"""
        return self.date_ended is None
    
    def clean(self):
        """Validate that end date is after join date"""
        from django.core.exceptions import ValidationError
        if self.date_joined and self.date_ended:
            if self.date_ended < self.date_joined:
                raise ValidationError({'date_ended': 'End date must be after join date.'})


class Recognition(models.Model):
    """Model for storing user recognitions and awards"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='recognitions')
    title = models.CharField(max_length=255)
    issuing_organization = models.CharField(max_length=255)
    date_received = models.DateField()
    description = models.TextField(blank=True, null=True)
    certificate_file = models.FileField(upload_to='achievements/', blank=True, null=True, help_text='Upload certificate or award document')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_received', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date_received']),
            models.Index(fields=['issuing_organization']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.title}"


class Training(models.Model):
    """Model for storing user trainings and seminars"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='trainings')
    title = models.CharField(max_length=255)
    organization = models.CharField(max_length=255)
    date_start = models.DateField()
    date_end = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    certificate_file = models.FileField(upload_to='achievements/', blank=True, null=True, help_text='Upload training certificate')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_start', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date_start']),
            models.Index(fields=['organization']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.title}"
    
    def clean(self):
        """Validate that end date is after start date"""
        from django.core.exceptions import ValidationError
        if self.date_start and self.date_end:
            if self.date_end < self.date_start:
                raise ValidationError({'date_end': 'End date must be after start date.'})


class Publication(models.Model):
    """Model for storing user publications"""
    PUBLICATION_TYPE_CHOICES = [
        ('journal', 'Journal Article'),
        ('conference', 'Conference Paper'),
        ('book', 'Book'),
        ('thesis', 'Thesis/Dissertation'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='publications')
    title = models.CharField(max_length=500)
    publication_type = models.CharField(max_length=20, choices=PUBLICATION_TYPE_CHOICES, default='journal')
    authors = models.CharField(max_length=500, help_text='List of authors')
    date_published = models.DateField()
    publisher = models.CharField(max_length=255, blank=True, null=True)
    url = models.URLField(blank=True, null=True, help_text='Link to publication')
    doi = models.CharField(max_length=100, blank=True, null=True, help_text='Digital Object Identifier')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_published', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date_published']),
            models.Index(fields=['publication_type']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.title}"


class Certificate(models.Model):
    """Model for storing professional certificates"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='certificates')
    certificate_type = models.CharField(max_length=255)
    certificate_number = models.CharField(max_length=100, blank=True, null=True)
    date_issued = models.DateField()
    expiry_date = models.DateField(blank=True, null=True)
    issuing_body = models.CharField(max_length=255)
    certificate_file = models.FileField(upload_to='achievements/', blank=True, null=True, help_text='Upload certificate document')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_issued', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date_issued']),
            models.Index(fields=['certificate_type']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.certificate_type}"
    
    @property
    def is_active(self):
        """Check if certificate is still valid"""
        if not self.expiry_date:
            return True
        return self.expiry_date >= timezone.now().date()


class CSEStatus(models.Model):
    """Model for storing Current Student Employment status"""
    STATUS_CHOICES = [
        ('employed', 'Employed'),
        ('unemployed', 'Unemployed'),
        ('self_employed', 'Self-Employed'),
        ('student', 'Student'),
        ('retired', 'Retired'),
    ]
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='cse_status')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unemployed')
    current_position = models.CharField(max_length=255, blank=True, null=True)
    current_company = models.CharField(max_length=255, blank=True, null=True)
    industry = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'CSE Status'
        verbose_name_plural = 'CSE Statuses'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_status_display()}"
    
    def clean(self):
        """Validate that end date is after start date"""
        from django.core.exceptions import ValidationError
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValidationError({'end_date': 'End date must be after start date.'})
