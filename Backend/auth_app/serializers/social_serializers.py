"""
Social networking serializers.
Contains FollowingSerializer for user connections and networking features.
"""
from rest_framework import serializers
from ..models import Following


class FollowingSerializer(serializers.ModelSerializer):
    """Serializer for Following/Connection model with detailed user information"""
    follower_name = serializers.CharField(source='follower.get_full_name', read_only=True)
    following_name = serializers.CharField(source='following.get_full_name', read_only=True)
    follower_profile_picture = serializers.ImageField(source='follower.profile_picture', read_only=True)
    following_profile_picture = serializers.ImageField(source='following.profile_picture', read_only=True)
    follower_headline = serializers.CharField(source='follower.profile.headline', read_only=True)
    following_headline = serializers.CharField(source='following.profile.headline', read_only=True)
    
    # Add detailed follower information
    follower_info = serializers.SerializerMethodField()
    following_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Following
        fields = ['id', 'follower', 'following', 'created_at', 'is_mutual', 'status',
                 'follower_name', 'following_name', 'follower_profile_picture', 'following_profile_picture',
                 'follower_headline', 'following_headline', 'follower_info', 'following_info']
        read_only_fields = ['created_at', 'is_mutual']
    
    def get_follower_info(self, obj):
        """Get detailed follower information"""
        # Get present address from Address model
        present_address = obj.follower.get_formatted_present_address()
        
        return {
            'id': obj.follower.id,
            'first_name': obj.follower.first_name,
            'last_name': obj.follower.last_name,
            'username': obj.follower.username,
            'profile_picture': obj.follower.profile_picture.url if obj.follower.profile_picture else None,
            'present_address': present_address,
            'profile': {
                'headline': obj.follower.profile.headline if hasattr(obj.follower, 'profile') else '',
                'present_occupation': obj.follower.profile.present_occupation if hasattr(obj.follower, 'profile') else '',
                'location': obj.follower.profile.location if hasattr(obj.follower, 'profile') else '',
            }
        }
    
    def get_following_info(self, obj):
        """Get detailed following information"""
        # Get present address from Address model
        present_address = obj.following.get_formatted_present_address()
        
        return {
            'id': obj.following.id,
            'first_name': obj.following.first_name,
            'last_name': obj.following.last_name,
            'username': obj.following.username,
            'profile_picture': obj.following.profile_picture.url if obj.following.profile_picture else None,
            'present_address': present_address,
            'profile': {
                'headline': obj.following.profile.headline if hasattr(obj.following, 'profile') else '',
                'present_occupation': obj.following.profile.present_occupation if hasattr(obj.following, 'profile') else '',
                'location': obj.following.profile.location if hasattr(obj.following, 'profile') else '',
            }
        }
