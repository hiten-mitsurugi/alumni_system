"""
Serializers package for auth_app.
This module exports all serializers for backward compatibility with existing imports.
"""

# Base serializers
from .base_serializers import (
    JSONField,
    AddressSerializer,
    AlumniDirectorySerializer
)

# Alumni serializers
from .alumni_serializers import (
    AlumniDirectoryCheckSerializer
)

# Skills and work serializers
from .skills_work_serializers import (
    SkillSerializer,
    UserSkillSerializer,
    WorkHistorySerializer
)

# Survey serializers
from .survey_serializers import (
    SkillsRelevanceSerializer,
    CurriculumRelevanceSerializer,
    PerceptionFurtherStudiesSerializer,
    FeedbackRecommendationsSerializer
)

# Registration serializers
from .registration_serializers import (
    RegisterSerializer,
    UserCreateSerializer
)

# Profile serializers
from .profile_serializers import (
    ProfileModelSerializer,
    ProfileSerializer,
    UserDetailSerializer,
    UserSearchSerializer,
    EnhancedProfileSerializer
)

# Social serializers
from .social_serializers import (
    FollowingSerializer
)

# Profile items serializers
from .profile_items_serializers import (
    AchievementSerializer,
    EducationSerializer,
    MembershipSerializer,
    RecognitionSerializer,
    TrainingSerializer,
    PublicationSerializer,
    CertificateSerializer,
    CSEStatusSerializer
)

# Enhanced user serializers
from .enhanced_user_serializers import (
    EnhancedUserDetailSerializer
)

# Privacy serializers
from .privacy_serializers import (
    FieldPrivacySettingSerializer,
    ProfileFieldUpdateSerializer
)

# Export all serializers
__all__ = [
    # Base serializers
    'JSONField',
    'AddressSerializer',
    'AlumniDirectorySerializer',
    
    # Alumni serializers
    'AlumniDirectoryCheckSerializer',
    
    # Skills and work serializers
    'SkillSerializer',
    'UserSkillSerializer',
    'WorkHistorySerializer',
    
    # Survey serializers
    'SkillsRelevanceSerializer',
    'CurriculumRelevanceSerializer',
    'PerceptionFurtherStudiesSerializer',
    'FeedbackRecommendationsSerializer',
    
    # Registration serializers
    'RegisterSerializer',
    'UserCreateSerializer',
    
    # Profile serializers
    'ProfileModelSerializer',
    'ProfileSerializer',
    'UserDetailSerializer',
    'UserSearchSerializer',
    'EnhancedProfileSerializer',
    
    # Social serializers
    'FollowingSerializer',
    
    # Profile items serializers
    'AchievementSerializer',
    'EducationSerializer',
    'MembershipSerializer',
    'RecognitionSerializer',
    'TrainingSerializer',
    'PublicationSerializer',
    'CertificateSerializer',
    'CSEStatusSerializer',
    
    # Enhanced user serializers
    'EnhancedUserDetailSerializer',
    
    # Privacy serializers
    'FieldPrivacySettingSerializer',
    'ProfileFieldUpdateSerializer',
]
