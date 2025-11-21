"""
Survey App Views - Modularized Structure
=========================================
This module organizes all survey-related views into logical components.
"""

# Admin Management Views
from .admin_views import (
    SurveyCategoryListCreateView,
    SurveyCategoryDetailView,
    SurveyQuestionListCreateView,
    SurveyQuestionDetailView,
    SurveyFormListCreateView,
    SurveyFormDetailView,
    SurveyFormPublishView,
    SurveyResponsesView,
)

# Alumni-Facing Views
from .alumni_views import (
    ActiveSurveyQuestionsView,
    SurveyResponseSubmitView,
    UserSurveyResponsesView,
    SurveyProgressView,
    RegistrationSurveyQuestionsView,
)

# Analytics Views
from .analytics_views import (
    SurveyResponseAnalyticsView,
    CategoryAnalyticsView,
    AnalyticsOverviewView,
    EmployabilityAnalyticsView,
    SkillsAnalyticsView,
    CurriculumAnalyticsView,
    StudiesAnalyticsView,
    CompetitivenessAnalyticsView,
    ProgramComparisonAnalyticsView,
    DemographicsAnalyticsView,
    AnalyticsFilterOptionsView,
    AnalyticsExportView,
    AnalyticsFullReportView,
)

# Export Views
from .export_views import (
    survey_export_view,
    category_analytics_pdf_export,
    form_analytics_pdf_export,
    clear_survey_cache_view,
)

# Distribution Views (Problem 1: Role Separation & Link Sharing)
from .distribution_views import (
    PublicSurveyDetailView,
)

# Monitoring Views (Problem 2: Non-Response Tracking)
from .monitoring_views import (
    SurveyNonRespondentsView,
    SurveyStatisticsView,
    AllSurveysStatisticsView,
)

__all__ = [
    # Admin Views
    'SurveyCategoryListCreateView',
    'SurveyCategoryDetailView',
    'SurveyQuestionListCreateView',
    'SurveyQuestionDetailView',
    'SurveyFormListCreateView',
    'SurveyFormDetailView',
    'SurveyFormPublishView',
    'SurveyResponsesView',
    
    # Alumni Views
    'ActiveSurveyQuestionsView',
    'SurveyResponseSubmitView',
    'UserSurveyResponsesView',
    'SurveyProgressView',
    'RegistrationSurveyQuestionsView',
    
    # Analytics Views
    'SurveyResponseAnalyticsView',
    'CategoryAnalyticsView',
    'AnalyticsOverviewView',
    'EmployabilityAnalyticsView',
    'SkillsAnalyticsView',
    'CurriculumAnalyticsView',
    'StudiesAnalyticsView',
    'CompetitivenessAnalyticsView',
    'ProgramComparisonAnalyticsView',
    'DemographicsAnalyticsView',
    'AnalyticsFilterOptionsView',
    'AnalyticsExportView',
    'AnalyticsFullReportView',
    
    # Export Views
    'survey_export_view',
    'category_analytics_pdf_export',
    'form_analytics_pdf_export',
    'clear_survey_cache_view',
    
    # Distribution Views
    'PublicSurveyDetailView',
    
    # Monitoring Views
    'SurveyNonRespondentsView',
    'SurveyStatisticsView',
    'AllSurveysStatisticsView',
]
