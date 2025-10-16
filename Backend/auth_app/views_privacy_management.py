"""
Privacy Management Views for per-field privacy controls
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.shortcuts import get_object_or_404

from .models_privacy import FieldPrivacySetting, VISIBILITY_CHOICES
from .privacy_mixins import ProfilePrivacyHelper


class PrivacySettingsView(APIView):
    """Get all privacy settings for the authenticated user"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get all privacy settings grouped by section"""
        try:
            # Get all privacy settings for the user
            settings = FieldPrivacySetting.objects.filter(user=request.user)
            
            # Group settings by section
            privacy_data = {
                'about': {},
                'contact': {},
                'education': {},
                'experience': {},
                'skills': {},
                'achievements': {}
            }
            
            # Map field names to sections
            field_sections = ProfilePrivacyHelper.get_field_section_mapping()
            
            for setting in settings:
                section = field_sections.get(setting.field_name, 'about')
                privacy_data[section][setting.field_name] = setting.visibility
            
            # Add defaults for fields without explicit settings
            all_fields = ProfilePrivacyHelper.get_all_privacy_fields()
            for section, fields in all_fields.items():
                for field in fields:
                    if field not in privacy_data[section]:
                        privacy_data[section][field] = 'public'  # Default visibility
            
            return Response({
                'privacy_settings': privacy_data,
                'visibility_options': [
                    {'value': choice[0], 'label': choice[1]} 
                    for choice in VISIBILITY_CHOICES
                ]
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to fetch privacy settings: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PrivacyFieldUpdateView(APIView):
    """Update privacy setting for a specific field"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Update privacy setting for a field"""
        try:
            field_name = request.data.get('field_name')
            visibility = request.data.get('visibility')
            
            if not field_name or not visibility:
                return Response(
                    {'error': 'field_name and visibility are required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate visibility choice
            valid_choices = [choice[0] for choice in VISIBILITY_CHOICES]
            if visibility not in valid_choices:
                return Response(
                    {'error': f'Invalid visibility choice. Valid options: {valid_choices}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate field name
            all_fields = ProfilePrivacyHelper.get_all_privacy_fields()
            valid_fields = []
            for section_fields in all_fields.values():
                valid_fields.extend(section_fields)
            
            if field_name not in valid_fields:
                return Response(
                    {'error': f'Invalid field name. Valid fields: {valid_fields}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update or create privacy setting
            setting, created = FieldPrivacySetting.objects.update_or_create(
                user=request.user,
                field_name=field_name,
                defaults={'visibility': visibility}
            )
            
            return Response({
                'field_name': field_name,
                'visibility': visibility,
                'updated': not created,
                'created': created
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to update privacy setting: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BulkPrivacyUpdateView(APIView):
    """Update multiple privacy settings at once"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Bulk update privacy settings"""
        try:
            settings = request.data.get('settings', {})
            
            if not settings:
                return Response(
                    {'error': 'settings object is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate all settings first
            valid_choices = [choice[0] for choice in VISIBILITY_CHOICES]
            all_fields = ProfilePrivacyHelper.get_all_privacy_fields()
            valid_fields = []
            for section_fields in all_fields.values():
                valid_fields.extend(section_fields)
            
            updates = []
            for field_name, visibility in settings.items():
                if field_name not in valid_fields:
                    return Response(
                        {'error': f'Invalid field name: {field_name}'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                if visibility not in valid_choices:
                    return Response(
                        {'error': f'Invalid visibility for {field_name}: {visibility}'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                updates.append((field_name, visibility))
            
            # Perform bulk update in transaction
            updated_count = 0
            created_count = 0
            
            with transaction.atomic():
                for field_name, visibility in updates:
                    setting, created = FieldPrivacySetting.objects.update_or_create(
                        user=request.user,
                        field_name=field_name,
                        defaults={'visibility': visibility}
                    )
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
            
            return Response({
                'updated': updated_count,
                'created': created_count,
                'total': len(updates)
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to update privacy settings: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SectionPrivacyUpdateView(APIView):
    """Update privacy settings for an entire section"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Set all fields in a section to the same visibility"""
        try:
            section = request.data.get('section')
            visibility = request.data.get('visibility')
            
            if not section or not visibility:
                return Response(
                    {'error': 'section and visibility are required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate visibility choice
            valid_choices = [choice[0] for choice in VISIBILITY_CHOICES]
            if visibility not in valid_choices:
                return Response(
                    {'error': f'Invalid visibility choice. Valid options: {valid_choices}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get fields for section
            all_fields = ProfilePrivacyHelper.get_all_privacy_fields()
            if section not in all_fields:
                return Response(
                    {'error': f'Invalid section. Valid sections: {list(all_fields.keys())}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            section_fields = all_fields[section]
            
            # Update all fields in section
            updated_count = 0
            created_count = 0
            
            with transaction.atomic():
                for field_name in section_fields:
                    setting, created = FieldPrivacySetting.objects.update_or_create(
                        user=request.user,
                        field_name=field_name,
                        defaults={'visibility': visibility}
                    )
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
            
            return Response({
                'section': section,
                'visibility': visibility,
                'updated': updated_count,
                'created': created_count,
                'fields_affected': section_fields
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to update section privacy: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PrivacyPreviewView(APIView):
    """Preview how profile looks with different privacy settings"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Preview profile data with temporary privacy settings"""
        try:
            # Get temporary privacy settings from request
            temp_settings = request.data.get('privacy_settings', {})
            viewer_type = request.data.get('viewer_type', 'public')  # public, alumni_only, connections_only
            
            # Get user's profile data
            from .serializers import EnhancedUserDetailSerializer
            serializer = EnhancedUserDetailSerializer(request.user, context={'request': request})
            profile_data = serializer.data
            
            # Apply temporary privacy filtering
            if temp_settings:
                # Create temporary privacy settings
                temp_privacy_map = {}
                for section, fields in temp_settings.items():
                    for field, visibility in fields.items():
                        temp_privacy_map[field] = visibility
                
                # Filter profile data based on viewer type and temporary settings
                if viewer_type != 'self':
                    profile_data = ProfilePrivacyHelper.apply_privacy_filter(
                        profile_data, 
                        temp_privacy_map, 
                        viewer_type
                    )
            
            return Response({
                'preview_data': profile_data,
                'viewer_type': viewer_type,
                'privacy_applied': bool(temp_settings)
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to generate privacy preview: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )