from .base import *


class SkillListCreateView(ListCreateAPIView):
    """List and create user skills"""
    permission_classes = [IsAuthenticated]
    serializer_class = SkillSerializer

    def get_queryset(self):
        return Skill.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WorkHistoryListCreateView(ListCreateAPIView):
    """List and create work history entries"""
    permission_classes = [IsAuthenticated]
    serializer_class = WorkHistorySerializer

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        if user_id:
            return WorkHistory.objects.filter(user_id=user_id)
        return WorkHistory.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WorkHistoryDetailView(RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete work history"""
    permission_classes = [IsAuthenticated]
    serializer_class = WorkHistorySerializer

    def get_queryset(self):
        return WorkHistory.objects.filter(user=self.request.user)


class AchievementListCreateView(ListCreateAPIView):
    """List and create achievements"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        try:
            from ..serializers import AchievementSerializer
            return AchievementSerializer
        except ImportError:
            # Fallback if Achievement model doesn't exist
            from rest_framework import serializers
            class DummySerializer(serializers.Serializer):
                pass
            return DummySerializer

    def get_queryset(self):
        try:
            from ..models import Achievement
            user_id = self.kwargs.get('user_id')
            if user_id:
                return Achievement.objects.filter(user_id=user_id)
            return Achievement.objects.filter(user=self.request.user)
        except ImportError:
            from django.db.models import QuerySet
            return QuerySet.none()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AchievementDetailView(RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete achievement"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        try:
            from ..serializers import AchievementSerializer
            return AchievementSerializer
        except ImportError:
            from rest_framework import serializers
            class DummySerializer(serializers.Serializer):
                pass
            return DummySerializer

    def get_queryset(self):
        try:
            from ..models import Achievement
            return Achievement.objects.filter(user=self.request.user)
        except ImportError:
            from django.db.models import QuerySet
            return QuerySet.none()


class EducationListCreateView(ListCreateAPIView):
    """List and create education entries"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        try:
            from ..serializers import EducationSerializer
            return EducationSerializer
        except ImportError:
            from rest_framework import serializers
            class DummySerializer(serializers.Serializer):
                pass
            return DummySerializer

    def get_queryset(self):
        try:
            from ..models import Education
            user_id = self.kwargs.get('user_id')
            if user_id:
                return Education.objects.filter(user_id=user_id)
            return Education.objects.filter(user=self.request.user)
        except ImportError:
            from django.db.models import QuerySet
            return QuerySet.none()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class EducationDetailView(RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete education entry"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        try:
            from ..serializers import EducationSerializer
            return EducationSerializer
        except ImportError:
            from rest_framework import serializers
            class DummySerializer(serializers.Serializer):
                pass
            return DummySerializer

    def get_queryset(self):
        try:
            from ..models import Education
            return Education.objects.filter(user=self.request.user)
        except ImportError:
            from django.db.models import QuerySet
            return QuerySet.none()