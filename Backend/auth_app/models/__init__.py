# Import all models to make them available when importing from auth_app.models
from .custom_user import CustomUser
from .alumni_directory import AlumniDirectory
from .skill import Skill
from .work_history import WorkHistory
from .skills_relevance import SkillsRelevance
from .curriculum_relevance import CurriculumRelevance
from .perception_further_studies import PerceptionFurtherStudies
from .feedback_recommendations import FeedbackRecommendations
from .profile import Profile
from .following import Following
from .achievement import Achievement
from .education import Education

__all__ = [
    'CustomUser',
    'AlumniDirectory',
    'Skill',
    'WorkHistory',
    'SkillsRelevance',
    'CurriculumRelevance',
    'PerceptionFurtherStudies',
    'FeedbackRecommendations',
    'Profile',
    'Following',
    'Achievement',
    'Education',
]