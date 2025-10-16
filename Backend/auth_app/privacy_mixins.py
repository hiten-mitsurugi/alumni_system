"""
Privacy mixins and utilities for field-level privacy controls
"""
from django.db.models import Q
from .models import FieldPrivacySetting, Following


class PrivacyFilterMixin:
    """Mixin to add privacy filtering capabilities to serializers and views"""
    
    @staticmethod
    def is_field_visible(field_name, target_user, viewer_user):
        """
        Check if a field should be visible to the viewer based on privacy settings
        
        Args:
            field_name: Name of the field to check
            target_user: User whose field is being viewed
            viewer_user: User who is viewing the field
            
        Returns:
            bool: True if field should be visible, False otherwise
        """
        # Own profile - always visible
        if target_user == viewer_user:
            return True
        
        # Get privacy setting for this field
        visibility = FieldPrivacySetting.get_user_field_visibility(target_user, field_name)
        
        if visibility == 'public':
            return True
        elif visibility == 'private':
            return False
        elif visibility == 'alumni_only':
            # Check if viewer is an approved alumni
            return (hasattr(viewer_user, 'is_approved') and 
                   viewer_user.is_approved and 
                   viewer_user.user_type == 3)
        elif visibility == 'connections_only':
            # Check if viewer is connected to target user
            return Following.objects.filter(
                follower=viewer_user,
                following=target_user,
                is_mutual=True,
                status='accepted'
            ).exists()
        
        return False
    
    @staticmethod
    def filter_field_data(data, field_mappings, target_user, viewer_user):
        """
        Filter data dictionary based on privacy settings
        
        Args:
            data: Dictionary of field data
            field_mappings: Dict mapping data keys to field names for privacy lookup
            target_user: User whose data is being viewed
            viewer_user: User viewing the data
            
        Returns:
            dict: Filtered data with only visible fields
        """
        if target_user == viewer_user:
            return data  # Own profile - return all data
        
        filtered_data = {}
        for key, value in data.items():
            field_name = field_mappings.get(key, key)  # Use mapping or key itself
            
            if PrivacyFilterMixin.is_field_visible(field_name, target_user, viewer_user):
                filtered_data[key] = value
        
        return filtered_data
    
    @staticmethod
    def filter_list_data(items_list, field_mappings, target_user, viewer_user):
        """
        Filter a list of items (like work histories, achievements) based on privacy
        
        Args:
            items_list: List of dictionaries or objects
            field_mappings: Dict mapping item fields to privacy field names
            target_user: User whose data is being viewed
            viewer_user: User viewing the data
            
        Returns:
            list: Filtered list with privacy-compliant items
        """
        if target_user == viewer_user:
            return items_list  # Own profile - return all data
        
        filtered_items = []
        for item in items_list:
            item_data = item if isinstance(item, dict) else item.__dict__
            filtered_item_data = {}
            include_item = False
            
            for key, value in item_data.items():
                if key.startswith('_'):  # Skip private attributes
                    continue
                    
                field_name = field_mappings.get(key, f"{key}")
                
                if PrivacyFilterMixin.is_field_visible(field_name, target_user, viewer_user):
                    filtered_item_data[key] = value
                    include_item = True
            
            # Only include item if at least some fields are visible
            if include_item:
                if isinstance(item, dict):
                    filtered_items.append(filtered_item_data)
                else:
                    # For model instances, create a filtered copy
                    filtered_items.append(type('FilteredItem', (), filtered_item_data))
        
        return filtered_items


class ProfilePrivacyHelper:
    """Helper class for profile-specific privacy operations"""
    
    # Field mappings for different sections
    BASIC_FIELDS = {
        'first_name': 'first_name',
        'last_name': 'last_name', 
        'middle_name': 'middle_name',
        'email': 'email',
        'contact_number': 'contact_number',
        'birth_date': 'birth_date',
        'gender': 'gender',
        'civil_status': 'civil_status',
        'profile_picture': 'profile_picture'
    }
    
    PROFILE_FIELDS = {
        'bio': 'bio',
        'headline': 'headline',
        'location': 'location',
        'summary': 'summary',
        'linkedin_url': 'linkedin_url',
        'facebook_url': 'facebook_url',
        'twitter_url': 'twitter_url',
        'instagram_url': 'instagram_url',
        'website_url': 'website_url',
        'present_occupation': 'present_occupation',
        'employing_agency': 'employing_agency',
        'present_employment_status': 'present_employment_status',
        'employment_classification': 'employment_classification'
    }
    
    WORK_HISTORY_FIELDS = {
        'occupation': 'work_occupation',
        'employing_agency': 'work_employing_agency',
        'start_date': 'work_start_date',
        'end_date': 'work_end_date',
        'job_type': 'work_job_type',
        'employment_classification': 'work_employment_classification',
        'location': 'work_location',
        'description': 'work_description'
    }
    
    EDUCATION_FIELDS = {
        'institution': 'education_institution',
        'degree_type': 'education_degree_type',
        'field_of_study': 'education_field_of_study',
        'start_date': 'education_start_date',
        'end_date': 'education_end_date',
        'is_current': 'education_is_current',
        'description': 'education_description'
    }
    
    ACHIEVEMENT_FIELDS = {
        'title': 'achievement_title',
        'organization': 'achievement_organization',
        'type': 'achievement_type',
        'date_received': 'achievement_date',
        'description': 'achievement_description',
        'url': 'achievement_url',
        'attachment': 'achievement_attachment',
        'is_featured': 'achievement_is_featured'
    }
    
    SKILL_FIELDS = {
        'name': 'skill_name',
        'proficiency_level': 'skill_proficiency',
        'years_of_experience': 'skill_years',
        'category': 'skill_category',
        'is_featured': 'skill_is_featured'
    }
    
    @classmethod
    def filter_user_data(cls, user_data, target_user, viewer_user):
        """Filter user basic data based on privacy"""
        return PrivacyFilterMixin.filter_field_data(
            user_data, cls.BASIC_FIELDS, target_user, viewer_user
        )
    
    @classmethod
    def filter_profile_data(cls, profile_data, target_user, viewer_user):
        """Filter profile data based on privacy"""
        return PrivacyFilterMixin.filter_field_data(
            profile_data, cls.PROFILE_FIELDS, target_user, viewer_user
        )
    
    @classmethod
    def filter_work_histories(cls, work_histories, target_user, viewer_user):
        """Filter work history data based on privacy"""
        return PrivacyFilterMixin.filter_list_data(
            work_histories, cls.WORK_HISTORY_FIELDS, target_user, viewer_user
        )
    
    @classmethod
    def filter_education(cls, education_list, target_user, viewer_user):
        """Filter education data based on privacy"""
        return PrivacyFilterMixin.filter_list_data(
            education_list, cls.EDUCATION_FIELDS, target_user, viewer_user
        )
    
    @classmethod
    def filter_achievements(cls, achievements, target_user, viewer_user):
        """Filter achievement data based on privacy"""
        return PrivacyFilterMixin.filter_list_data(
            achievements, cls.ACHIEVEMENT_FIELDS, target_user, viewer_user
        )
    
    @classmethod
    def filter_skills(cls, skills, target_user, viewer_user):
        """Filter skill data based on privacy"""
        return PrivacyFilterMixin.filter_list_data(
            skills, cls.SKILL_FIELDS, target_user, viewer_user
        )


def get_default_privacy_settings():
    """Get default privacy settings for new users"""
    return {
        # Basic fields - alumni only by default
        'first_name': 'alumni_only',
        'last_name': 'alumni_only',
        'middle_name': 'private',
        'email': 'connections_only',
        'contact_number': 'private',
        'birth_date': 'private',
        'gender': 'alumni_only',
        'civil_status': 'alumni_only',
        'profile_picture': 'alumni_only',
        
        # Profile fields - alumni only by default
        'bio': 'alumni_only',
        'headline': 'alumni_only',
        'location': 'alumni_only',
        'summary': 'alumni_only',
        'linkedin_url': 'alumni_only',
        'facebook_url': 'private',
        'twitter_url': 'private',
        'instagram_url': 'private',
        'website_url': 'alumni_only',
        'present_occupation': 'alumni_only',
        'employing_agency': 'alumni_only',
        
        # Work history - connections only by default
        'work_occupation': 'connections_only',
        'work_employing_agency': 'connections_only',
        'work_start_date': 'connections_only',
        'work_end_date': 'connections_only',
        
        # Education - alumni only by default
        'education_institution': 'alumni_only',
        'education_degree_type': 'alumni_only',
        'education_field_of_study': 'alumni_only',
        'education_start_date': 'alumni_only',
        'education_end_date': 'alumni_only',
        
        # Achievements - alumni only by default
        'achievement_title': 'alumni_only',
        'achievement_organization': 'alumni_only',
        'achievement_type': 'alumni_only',
        'achievement_date': 'alumni_only',
        
        # Skills - alumni only by default
        'skill_name': 'alumni_only',
        'skill_proficiency': 'connections_only',
        'skill_years': 'connections_only'
    }