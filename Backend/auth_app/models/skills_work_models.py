"""
Skills, Work History, and Survey Models
"""
from .base_models import *
from .user_models import CustomUser

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
    
    # Fields matching actual database structure
    job_type = models.CharField(max_length=100, blank=True, null=True)
    employment_status = models.CharField(max_length=100, blank=True, null=True)
    classification = models.CharField(max_length=50, choices=CLASSIFICATION_CHOICES)
    occupation = models.CharField(max_length=255)
    employing_agency = models.CharField(max_length=255)
    how_got_job = models.CharField(max_length=255, blank=True, null=True)
    monthly_income = models.CharField(max_length=100, blank=True, null=True)
    is_breadwinner = models.BooleanField(default=False)
    # Normalized relation to Skill instead of storing skills as text
    skills = models.ManyToManyField(Skill, related_name='work_histories', blank=True)
    # Explicit flag for current job (optional - can be inferred from end_date==None)
    is_current_job = models.BooleanField(default=False)
    length_of_service = models.CharField(max_length=50, blank=True, null=True)
    college_education_relevant = models.CharField(max_length=100, blank=True, null=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    
    # Note: is_current_job and skills fields don't exist in database
    # They may be in serializer for frontend compatibility but not stored

    def __str__(self):
        return f"{self.occupation} at {self.employing_agency}"


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
