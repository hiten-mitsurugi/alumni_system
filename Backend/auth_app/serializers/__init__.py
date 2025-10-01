# Import all serializer classes to make them available when importing from auth_app.serializers

# Base utility classes and fields
from .base import AddressSerializer, JSONField

# Alumni directory related serializers
from .alumni_directory_check import AlumniDirectoryCheckSerializer
from .alumni_directory import AlumniDirectorySerializer

# Model-specific serializers
from .skill import SkillSerializer
from .work_history import WorkHistorySerializer
from .skills_relevance import SkillsRelevanceSerializer
from .curriculum_relevance import CurriculumRelevanceSerializer
from .perception_further_studies import PerceptionFurtherStudiesSerializer
from .feedback_recommendations import FeedbackRecommendationsSerializer

# User registration and creation serializers
from .register import RegisterSerializer
from .user_create import UserCreateSerializer

# Profile related serializers
from .profile_model import ProfileModelSerializer
from .profile import ProfileSerializer

# User detail serializers
from .user_detail import UserDetailSerializer
from .user_search import UserSearchSerializer

# Social feature serializers (LinkedIn-style)
from .following import FollowingSerializer
from .achievement import AchievementSerializer
from .education import EducationSerializer

# Enhanced profile serializers
from .enhanced_profile import EnhancedProfileSerializer
from .enhanced_user_detail import EnhancedUserDetailSerializer

# Make all serializers available for import
__all__ = [
    # Base utilities
    'AddressSerializer',
    'JSONField',
    
    # Alumni directory
    'AlumniDirectoryCheckSerializer',
    'AlumniDirectorySerializer',
    
    # Model serializers
    'SkillSerializer',
    'WorkHistorySerializer',
    'SkillsRelevanceSerializer',
    'CurriculumRelevanceSerializer',
    'PerceptionFurtherStudiesSerializer',
    'FeedbackRecommendationsSerializer',
    
    # User serializers
    'RegisterSerializer',
    'UserCreateSerializer',
    
    # Profile serializers
    'ProfileModelSerializer',
    'ProfileSerializer',
    
    # User detail serializers
    'UserDetailSerializer',
    'UserSearchSerializer',
    
    # Social feature serializers
    'FollowingSerializer',
    'AchievementSerializer',
    'EducationSerializer',
    
    # Enhanced serializers
    'EnhancedProfileSerializer',
    'EnhancedUserDetailSerializer',
]