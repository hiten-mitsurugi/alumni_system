# Field Privacy and Profile Update Views
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .serializers import ProfileFieldUpdateSerializer, FieldPrivacySettingSerializer

class ProfileFieldUpdateView(APIView):
    """API view for updating individual profile fields with privacy settings"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get all field privacy settings for the user"""
        from .models import FieldPrivacySetting
        settings = FieldPrivacySetting.objects.filter(user=request.user)
        serializer = FieldPrivacySettingSerializer(settings, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """Update a profile field value and/or its privacy setting"""
        from .models import FieldPrivacySetting, Profile, CustomUser
        
        serializer = ProfileFieldUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        field_name = serializer.validated_data['field_name']
        field_value = serializer.validated_data.get('field_value')
        visibility = serializer.validated_data.get('visibility', 'alumni_only')
        
        try:
            # Update field privacy setting
            FieldPrivacySetting.set_user_field_visibility(
                request.user, field_name, visibility
            )
            
            # Update field value if provided
            if field_value is not None:
                # Handle address fields
                if field_name in ['present_address', 'permanent_address']:
                    from .models import Address
                    address_category = field_name.replace('_address', '')
                    
                    # For now, we'll treat field_value as the full formatted address
                    # In a full implementation, you might want to parse this or handle structured data
                    address, created = Address.objects.get_or_create(
                        user=request.user,
                        address_category=address_category,
                        defaults={
                            'address_type': 'philippines',
                            'full_address': field_value,
                            'normalized_text': field_value
                        }
                    )
                    if not created:
                        # Clear structured fields to ensure full_address is used
                        address.street_address = None
                        address.barangay = None
                        address.city_name = None
                        address.province_name = None
                        address.region_name = None
                        address.postal_code = None
                        # Set the full address
                        address.full_address = field_value
                        address.normalized_text = field_value
                        address.save()
                
                # Check if field is in CustomUser model
                elif hasattr(CustomUser, field_name):
                    setattr(request.user, field_name, field_value)
                    request.user.save()
                # Check if field is in Profile model
                else:
                    profile, created = Profile.objects.get_or_create(user=request.user)
                    if hasattr(Profile, field_name):
                        setattr(profile, field_name, field_value)
                        profile.save()
                    else:
                        return Response(
                            {'error': f'Field {field_name} not found'}, 
                            status=status.HTTP_400_BAD_REQUEST
                        )
            
            return Response({
                'message': 'Field updated successfully',
                'field_name': field_name,
                'visibility': visibility
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProfileAboutDataView(APIView):
    """API view to get comprehensive profile data for About section"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id=None):
        """Get comprehensive profile data with privacy settings"""
        from .models import FieldPrivacySetting, Profile, CustomUser
        
        # Get target user (self or other user)
        if user_id:
            target_user = get_object_or_404(CustomUser, id=user_id)
            is_own_profile = target_user == request.user
        else:
            target_user = request.user
            is_own_profile = True
        
        # Get profile or create if doesn't exist
        profile, created = Profile.objects.get_or_create(user=target_user)
        
        # Define all available fields from both models
        user_fields = [
            'first_name', 'last_name', 'middle_name', 'email', 'username',
            'contact_number', 'birth_date', 'sex', 'gender', 'civil_status',
            'employment_status', 'program', 'year_graduated',
            'mothers_name', 'mothers_occupation', 'fathers_name', 'fathers_occupation'
        ]
        
        profile_fields = [
            'bio', 'headline', 'location', 'summary', 'mobile_number',
            'present_employment_status', 'employment_classification',
            'present_occupation', 'employing_agency',
            'linkedin_url', 'facebook_url', 'twitter_url', 'instagram_url', 'website_url'
        ]
        
        # Compile field data with privacy settings
        field_data = {}
        
        # Process CustomUser fields
        for field_name in user_fields:
            value = getattr(target_user, field_name, None)
            # Format dates and choices properly
            if field_name == 'birth_date' and value:
                value = value.strftime('%Y-%m-%d')
            elif field_name in ['sex', 'gender', 'civil_status', 'employment_status']:
                # Get display value for choice fields
                display_method = f'get_{field_name}_display'
                if hasattr(target_user, display_method):
                    display_value = getattr(target_user, display_method)()
                    value = {'value': value, 'display': display_value}
            
            # Get privacy setting
            visibility = FieldPrivacySetting.get_user_field_visibility(target_user, field_name)
            
            field_data[field_name] = {
                'value': value,
                'visibility': visibility,
                'is_visible': is_own_profile or self._is_field_visible(visibility, request.user, target_user),
                'field_type': 'user'
            }
        
        # Process Profile fields
        for field_name in profile_fields:
            value = getattr(profile, field_name, None)
            visibility = FieldPrivacySetting.get_user_field_visibility(target_user, field_name)
            
            field_data[field_name] = {
                'value': value,
                'visibility': visibility,
                'is_visible': is_own_profile or self._is_field_visible(visibility, request.user, target_user),
                'field_type': 'profile'
            }
        
        # Get addresses - always include address fields even if empty
        present_address = target_user.normalized_addresses.filter(address_category='present').first()
        permanent_address = target_user.normalized_addresses.filter(address_category='permanent').first()
        
        # Always include present_address field
        field_data['present_address'] = {
            'value': present_address.get_formatted_address() if present_address else '',
            'visibility': FieldPrivacySetting.get_user_field_visibility(target_user, 'present_address'),
            'is_visible': is_own_profile or self._is_field_visible(
                FieldPrivacySetting.get_user_field_visibility(target_user, 'present_address'),
                request.user, target_user
            ),
            'field_type': 'address'
        }
        
        # Always include permanent_address field
        field_data['permanent_address'] = {
            'value': permanent_address.get_formatted_address() if permanent_address else '',
            'visibility': FieldPrivacySetting.get_user_field_visibility(target_user, 'permanent_address'),
            'is_visible': is_own_profile or self._is_field_visible(
                FieldPrivacySetting.get_user_field_visibility(target_user, 'permanent_address'),
                request.user, target_user
            ),
            'field_type': 'address'
        }
        
        # Transform field_data to a more frontend-friendly format
        user_data = {}
        profile_data = {}
        
        for field_name, field_info in field_data.items():
            if field_info['is_visible']:
                value = field_info['value']
                # Handle choice fields - extract just the value, not the display
                if isinstance(value, dict) and 'value' in value:
                    value = value['value']
                
                if field_info['field_type'] == 'user':
                    user_data[field_name] = value
                elif field_info['field_type'] == 'profile':
                    profile_data[field_name] = value
                elif field_info['field_type'] == 'address':
                    # Keep addresses in user_data for now, they'll be fetched separately
                    user_data[field_name] = value
        
        return Response({
            'user_id': target_user.id,
            'is_own_profile': is_own_profile,
            'user': user_data,
            'profile': profile_data,
            'field_data': field_data,  # Keep this for compatibility
            'visibility_choices': FieldPrivacySetting.VISIBILITY_CHOICES
        })
    
    def _is_field_visible(self, visibility, viewer_user, target_user):
        """Check if a field should be visible based on privacy settings"""
        if visibility == 'public':
            return True
        elif visibility == 'private':
            return False
        elif visibility == 'alumni_only':
            # Check if viewer is an approved alumni
            return viewer_user.is_approved and viewer_user.user_type == 3
        elif visibility == 'connections_only':
            # Check if viewer is connected to target user
            from .models import Following
            return Following.objects.filter(
                follower=viewer_user,
                following=target_user,
                is_mutual=True,
                status='accepted'
            ).exists()
        return False


class UserAddressesView(APIView):
    """API view to get user addresses with privacy settings"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id):
        """Get user addresses with privacy settings"""
        from .models import CustomUser, Address, FieldPrivacySetting
        
        # Get target user
        target_user = get_object_or_404(CustomUser, id=user_id)
        is_own_profile = target_user == request.user
        
        # Get all addresses for the user
        addresses = Address.objects.filter(user=target_user)
        
        result_addresses = []
        for address in addresses:
            # Check privacy settings for address visibility
            field_name = f"{address.address_category}_address"
            visibility = FieldPrivacySetting.get_user_field_visibility(target_user, field_name)
            is_visible = is_own_profile or self._is_field_visible(visibility, request.user, target_user)
            
            if is_visible:
                result_addresses.append({
                    'id': address.id,
                    'address_category': address.address_category,
                    'address_type': address.address_type,
                    'street_address': address.street_address,
                    'barangay': address.barangay,
                    'city_municipality': address.city_municipality,
                    'province': address.province,
                    'region': address.region,
                    'postal_code': address.postal_code,
                    'city': address.city,
                    'state_province': address.state_province,
                    'country': address.country,
                    'formatted_address': address.get_formatted_address()
                })
        
        return Response(result_addresses)
    
    def _is_field_visible(self, visibility, viewer_user, target_user):
        """Check if a field should be visible based on privacy settings"""
        if visibility == 'public':
            return True
        elif visibility == 'private':
            return False
        elif visibility == 'alumni_only':
            # Check if viewer is an approved alumni
            return viewer_user.is_approved and viewer_user.user_type == 3
        elif visibility == 'connections_only':
            # Check if viewer is connected to target user
            from .models import Following
            return Following.objects.filter(
                follower=viewer_user,
                following=target_user,
                is_mutual=True,
                status='accepted'
            ).exists()
        return False