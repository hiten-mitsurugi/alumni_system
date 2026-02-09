"""
Models Package - Exports all models for backward compatibility
"""
from .user_models import CustomUser, Address, AlumniDirectory
from .skills_work_models import (
    Skill, UserSkill, WorkHistory, SkillsRelevance, 
    CurriculumRelevance, PerceptionFurtherStudies, FeedbackRecommendations
)
from .profile_social_models import Profile, Following, Achievement, Education
from .privacy_models import FieldPrivacySetting, SectionPrivacySetting
from .professional_models import (
    Membership, Recognition, Training, Publication, Certificate, CSEStatus
)

__all__ = [
    'CustomUser', 'Address', 'AlumniDirectory',
    'Skill', 'UserSkill', 'WorkHistory', 'SkillsRelevance',
    'CurriculumRelevance', 'PerceptionFurtherStudies', 'FeedbackRecommendations',
    'Profile', 'Following', 'Achievement', 'Education',
    'FieldPrivacySetting', 'SectionPrivacySetting',
    'Membership', 'Recognition', 'Training', 'Publication', 'Certificate', 'CSEStatus',
]
