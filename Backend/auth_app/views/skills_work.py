"""
Skills and Work History Views - Skills, Work History, Achievements, Education CRUD operations
"""
from .base_imports import *
from auth_app.models import Membership, Recognition, Training, Publication, Certificate, CSEStatus
from auth_app.serializers import MembershipSerializer, RecognitionSerializer, TrainingSerializer, PublicationSerializer, CertificateSerializer, CSEStatusSerializer

class SkillListCreateView(ListCreateAPIView):
    serializer_class = SkillSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        cache_key = 'skills_list'
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        queryset = list(Skill.objects.all())
        cache.set(cache_key, queryset, timeout=3600)
        return queryset


class UserSkillListCreateView(ListCreateAPIView):
    """List and create user skills for authenticated user or view other user's skills"""
    serializer_class = UserSkillSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Check if viewing another user's skills
        user_id = self.kwargs.get('user_id') or self.request.query_params.get('user_id')
        
        if user_id:
            # Viewing another user's skills
            cache_key = f'user_skills_{user_id}'
            cached_data = cache.get(cache_key)
            if cached_data:
                return cached_data
            queryset = UserSkill.objects.filter(user_id=user_id).order_by('category', 'name')
            cache.set(cache_key, list(queryset), timeout=3600)
            return queryset
        else:
            # Current user's skills
            cache_key = f'user_skills_{self.request.user.id}'
            cached_data = cache.get(cache_key)
            if cached_data:
                return cached_data
            queryset = UserSkill.objects.filter(user=self.request.user).order_by('category', 'name')
            cache.set(cache_key, list(queryset), timeout=3600)
            return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        # Clear cache after creating new skill
        cache.delete(f'user_skills_{self.request.user.id}')


class UserSkillDetailView(RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a specific user skill"""
    serializer_class = UserSkillSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserSkill.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save()
        # Clear cache after updating skill
        cache.delete(f'user_skills_{self.request.user.id}')

    def perform_destroy(self, instance):
        user_id = instance.user.id
        instance.delete()
        # Clear cache after deleting skill
        cache.delete(f'user_skills_{user_id}')


class WorkHistoryListCreateView(ListCreateAPIView):
    serializer_class = WorkHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        cache_key = f'work_history_{self.request.user.id}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        queryset = WorkHistory.objects.filter(user=self.request.user)
        cache.set(cache_key, list(queryset), timeout=3600)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        # Clear cache after creating new work history
        cache.delete(f'work_history_{self.request.user.id}')


class WorkHistoryDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = WorkHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WorkHistory.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save()
        # Clear cache after updating work history
        cache.delete(f'work_history_{self.request.user.id}')

    def perform_destroy(self, instance):
        user_id = instance.user.id
        instance.delete()
        # Clear cache after deleting work history
        cache.delete(f'work_history_{user_id}')


class AchievementListCreateView(ListCreateAPIView):
    """List and create achievements for authenticated user or specific user"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        # Import here to avoid circular imports
        from auth_app.models import Achievement
        from rest_framework import serializers
        
        class AchievementSerializer(serializers.ModelSerializer):
            class Meta:
                model = Achievement
                fields = '__all__'
                read_only_fields = ['user', 'created_at', 'updated_at']
                
        return AchievementSerializer
    
    def get_queryset(self):
        # Import here to avoid circular imports
        from auth_app.models import Achievement
        
        user_id = self.kwargs.get('user_id') or self.request.query_params.get('user_id')
        if user_id:
            return Achievement.objects.filter(user_id=user_id)
        return Achievement.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AchievementDetailView(RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a specific achievement"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        # Import here to avoid circular imports
        from auth_app.models import Achievement
        from rest_framework import serializers
        
        class AchievementSerializer(serializers.ModelSerializer):
            class Meta:
                model = Achievement
                fields = '__all__'
                read_only_fields = ['user', 'created_at', 'updated_at']
                
        return AchievementSerializer
    
    def get_queryset(self):
        # Import here to avoid circular imports
        from auth_app.models import Achievement
        return Achievement.objects.filter(user=self.request.user)


class EducationListCreateView(ListCreateAPIView):
    """List and create education records for authenticated user or specific user"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        # Import here to avoid circular imports
        from auth_app.models import Education
        from rest_framework import serializers
        
        class EducationSerializer(serializers.ModelSerializer):
            class Meta:
                model = Education
                fields = ['id', 'institution', 'degree_type', 'field_of_study', 'start_date', 'end_date', 'is_current', 'description', 'user']
                read_only_fields = ['user']
                
        return EducationSerializer
    
    def get_queryset(self):
        # Import here to avoid circular imports
        from auth_app.models import Education
        
        user_id = self.kwargs.get('user_id') or self.request.query_params.get('user_id')
        if user_id:
            return Education.objects.filter(user_id=user_id)
        return Education.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class EducationDetailView(RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a specific education record"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        # Import here to avoid circular imports
        from auth_app.models import Education
        from rest_framework import serializers
        
        class EducationSerializer(serializers.ModelSerializer):
            class Meta:
                model = Education
                fields = ['id', 'institution', 'degree_type', 'field_of_study', 'start_date', 'end_date', 'is_current', 'description', 'user']
                read_only_fields = ['user']
                
        return EducationSerializer
    
    def get_queryset(self):
        # Import here to avoid circular imports
        from auth_app.models import Education
        return Education.objects.filter(user=self.request.user)


class MembershipListCreateView(ListCreateAPIView):
    """List and create organization memberships for authenticated user"""
    serializer_class = MembershipSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Check if viewing another user's memberships
        user_id = self.kwargs.get('user_id')
        
        if user_id:
            # Viewing another user's memberships (with privacy filtering in enhanced-profile)
            return Membership.objects.filter(user_id=user_id).order_by('-date_joined', '-created_at')
        else:
            # Current user's memberships
            return Membership.objects.filter(user=self.request.user).order_by('-date_joined', '-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MembershipDetailView(RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a specific membership"""
    serializer_class = MembershipSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Membership.objects.filter(user=self.request.user)


class RecognitionListCreateView(ListCreateAPIView):
    """List or create recognitions"""
    serializer_class = RecognitionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        if user_id:
            return Recognition.objects.filter(user_id=user_id)
        return Recognition.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RecognitionDetailView(RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a specific recognition"""
    serializer_class = RecognitionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Recognition.objects.filter(user=self.request.user)


class TrainingListCreateView(ListCreateAPIView):
    """List or create trainings"""
    serializer_class = TrainingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        if user_id:
            return Training.objects.filter(user_id=user_id)
        return Training.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TrainingDetailView(RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a specific training"""
    serializer_class = TrainingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Training.objects.filter(user=self.request.user)


class PublicationListCreateView(ListCreateAPIView):
    """List or create publications"""
    serializer_class = PublicationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        if user_id:
            return Publication.objects.filter(user_id=user_id)
        return Publication.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PublicationDetailView(RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a specific publication"""
    serializer_class = PublicationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Publication.objects.filter(user=self.request.user)


class CertificateListCreateView(ListCreateAPIView):
    """List or create certificates"""
    serializer_class = CertificateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        if user_id:
            return Certificate.objects.filter(user_id=user_id)
        return Certificate.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CertificateDetailView(RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a specific certificate"""
    serializer_class = CertificateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Certificate.objects.filter(user=self.request.user)


class CSEStatusView(RetrieveUpdateAPIView):
    """Retrieve or update CSE status (one per user)"""
    serializer_class = CSEStatusSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        obj, created = CSEStatus.objects.get_or_create(user=self.request.user)
        return obj

