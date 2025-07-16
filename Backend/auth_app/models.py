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
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True, null=True)
    civil_status = models.CharField(max_length=20, choices=CIVIL_STATUS_CHOICES, blank=True, null=True)
    employment_status = models.CharField(max_length=100, choices=EMPLOYMENT_STATUS_CHOICES, blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    email = models.EmailField(_('email address'), unique=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    middle_name = models.CharField(max_length=150, blank=True, null=True)
    school_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    government_id = models.FileField(upload_to='government_ids/', null=True, blank=True)
    program = models.CharField(max_length=100, blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    year_graduated = models.PositiveIntegerField(blank=True, null=True)
    present_address = models.TextField(blank=True, null=True)
    permanent_address = models.TextField(blank=True, null=True)
    mothers_name = models.CharField(max_length=150, blank=True, null=True)
    mothers_occupation = models.CharField(max_length=100, blank=True, null=True)
    fathers_name = models.CharField(max_length=150, blank=True, null=True)
    fathers_occupation = models.CharField(max_length=100, blank=True, null=True)

    REQUIRED_FIELDS = ['email', 'school_id', 'first_name', 'last_name', 'password', 'program']

    class Meta:
        indexes = [
            models.Index(fields=['user_type', 'is_approved']),
            models.Index(fields=['school_id']),
        ]

    def __str__(self):
        return self.username

class AlumniDirectory(models.Model):
    first_name = models.CharField(max_length=150)
    middle_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150)
    birth_date = models.DateField()
    school_id = models.CharField(max_length=50, unique=True)
    program = models.CharField(max_length=100)
    year_graduated = models.PositiveIntegerField()
    gender = models.CharField(max_length=20, choices=CustomUser.GENDER_CHOICES)

    class Meta:
        indexes = [
            models.Index(fields=['school_id']),
            models.Index(fields=['first_name', 'last_name']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.school_id})"

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    def __str__(self):
        return self.name

class WorkHistory(models.Model):
    EMPLOYMENT_STATUS_CHOICES = CustomUser.EMPLOYMENT_STATUS_CHOICES
    CLASSIFICATION_CHOICES = (
        ('government', 'Government'),
        ('private', 'Private'),
        ('ngo', 'NGO'),
        ('freelance', 'Freelance'),
        ('business_owner', 'Business Owner'),
    )
    INCOME_CHOICES = (
        ('less_than_15000', 'Less than P15,000'),
        ('15000_to_29999', 'P15,000 - P29,999'),
        ('30000_to_49999', 'P30,000 - P49,999'),
        ('50000_and_above', 'P50,000 and above'),
        ('prefer_not_to_say', 'Prefer not to say'),
    )
    RELEVANCE_CHOICES = (
        ('yes', 'Yes'),
        ('no', 'No'),
        ('somewhat', 'Somewhat'),
    )
    JOB_TYPE_CHOICES = (
        ('first_job', 'First Job'),
        ('current_job', 'Current Job'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='work_histories')
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    employment_status = models.CharField(max_length=50, choices=EMPLOYMENT_STATUS_CHOICES)
    classification = models.CharField(max_length=50, choices=CLASSIFICATION_CHOICES)
    occupation = models.CharField(max_length=255)
    employing_agency = models.CharField(max_length=255)
    how_got_job = models.CharField(max_length=100)
    monthly_income = models.CharField(max_length=50, choices=INCOME_CHOICES)
    is_breadwinner = models.BooleanField()
    length_of_service = models.CharField(max_length=50)
    college_education_relevant = models.CharField(max_length=10, choices=RELEVANCE_CHOICES)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    skills = models.ManyToManyField(Skill, related_name='work_histories', blank=True)

    def __str__(self):
        return f"{self.occupation} at {self.employing_agency} ({self.job_type})"

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
    full_name = models.CharField(max_length=450)
    email_address = models.EmailField()
    school_id = models.CharField(max_length=50)
    mobile_number = models.CharField(max_length=20)
    sex = models.CharField(max_length=20, choices=CustomUser.GENDER_CHOICES)
    civil_status = models.CharField(max_length=20, choices=CustomUser.CIVIL_STATUS_CHOICES)
    year_of_birth = models.DateField()
    present_address = models.TextField()
    permanent_address = models.TextField()
    mothers_name = models.CharField(max_length=150)
    mothers_occupation = models.CharField(max_length=100)
    fathers_name = models.CharField(max_length=150)
    fathers_occupation = models.CharField(max_length=100)
    year_graduated = models.PositiveIntegerField()
    program = models.CharField(max_length=100)
    present_employment_status = models.CharField(max_length=50, choices=CustomUser.EMPLOYMENT_STATUS_CHOICES)
    employment_classification = models.CharField(max_length=50, choices=WorkHistory.CLASSIFICATION_CHOICES, blank=True)
    present_occupation = models.CharField(max_length=255, blank=True)
    employing_agency = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=[('online', 'Online'), ('offline', 'Offline')], default='offline')  # Added
    bio = models.TextField(blank=True, null=True)  # Added
    last_seen = models.DateTimeField(null=True, blank=True)  # Added

    def save(self, *args, **kwargs):
        self.full_name = f"{self.user.first_name} {self.user.middle_name or ''} {self.user.last_name}".strip()
        self.email_address = self.user.email
        self.school_id = self.user.school_id
        self.mobile_number = self.user.contact_number
        self.sex = self.user.gender
        self.civil_status = self.user.civil_status
        self.year_of_birth = self.user.birth_date
        self.present_address = self.user.present_address
        self.permanent_address = self.user.permanent_address
        self.mothers_name = self.user.mothers_name
        self.mothers_occupation = self.user.mothers_occupation
        self.fathers_name = self.user.fathers_name
        self.fathers_occupation = self.user.fathers_occupation
        self.year_graduated = self.user.year_graduated
        self.program = self.user.program
        current_job = self.user.work_histories.filter(job_type='current_job').first()
        if current_job:
            self.present_employment_status = current_job.employment_status
            self.employment_classification = current_job.classification
            self.present_occupation = current_job.occupation
            self.employing_agency = current_job.employing_agency
        super().save(*args, **kwargs)