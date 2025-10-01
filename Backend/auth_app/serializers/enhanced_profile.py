from rest_framework import serializers
from ..models import Profile, Following


class EnhancedProfileSerializer(serializers.ModelSerializer):
    """Enhanced Profile serializer with LinkedIn-style features"""
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    connections_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    is_followed_by = serializers.SerializerMethodField()
    mutual_connection = serializers.SerializerMethodField()
    
    class Meta:
        model = Profile
        fields = '__all__'
        read_only_fields = ['user', 'timestamp']
    
    def get_followers_count(self, obj):
        return obj.get_followers_count()
    
    def get_following_count(self, obj):
        return obj.get_following_count()
    
    def get_connections_count(self, obj):
        return obj.get_connections_count()
    
    def get_is_following(self, obj):
        """Check if current user is following this profile's user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user != obj.user:
            return Following.objects.filter(follower=request.user, following=obj.user).exists()
        return False
    
    def get_is_followed_by(self, obj):
        """Check if this profile's user is following current user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user != obj.user:
            return Following.objects.filter(follower=obj.user, following=request.user).exists()
        return False
    
    def get_mutual_connection(self, obj):
        """Check if there's a mutual connection"""
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user != obj.user:
            return Following.objects.filter(
                follower=request.user, 
                following=obj.user, 
                is_mutual=True
            ).exists()
        return False