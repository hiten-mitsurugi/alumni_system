"""
Temporary simple profile view for profile picture functionality
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from auth_app.models import CustomUser

class SimpleProfileView(APIView):
    """Simple profile view that returns just basic user data and profile picture"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id=None):
        # Handle different lookup methods
        if user_id:
            try:
                user = CustomUser.objects.get(id=user_id, is_approved=True, is_active=True)
            except CustomUser.DoesNotExist:
                return Response({'error': 'User not found'}, status=404)
        else:
            user = request.user
        
        # Return minimal profile data
        profile_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'profile_picture': user.profile_picture.url if user.profile_picture else None,
            'contact_number': user.contact_number or '',
            'program': user.program or '',
            'user_type': user.user_type,
            'is_approved': user.is_approved,
            'is_active': user.is_active,
        }
        
        # Add basic profile info if available
        if hasattr(user, 'profile') and user.profile:
            profile = user.profile
            profile_data.update({
                'profile': {
                    'bio': profile.bio or '',
                    'location': profile.location or '',
                    'website': profile.website or '',
                    'birth_date': profile.birth_date.isoformat() if profile.birth_date else None,
                    'linkedin_url': profile.linkedin_url or '',
                    'twitter_url': profile.twitter_url or '',
                    'facebook_url': profile.facebook_url or '',
                    'instagram_url': profile.instagram_url or '',
                    'present_occupation': profile.present_occupation or '',
                    'employing_agency': profile.employing_agency or '',
                }
            })
        
        return Response(profile_data)