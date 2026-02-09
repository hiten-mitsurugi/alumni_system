"""
Survey and profile-related views for questionnaire data collection
Handles Address, Skills Relevance, Curriculum Relevance, Perception Studies, and Feedback
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from django.shortcuts import get_object_or_404

from ..models import (
    Address, SkillsRelevance, CurriculumRelevance, 
    PerceptionFurtherStudies, FeedbackRecommendations, Following
)
from ..serializers import (
    AddressSerializer, SkillsRelevanceSerializer, CurriculumRelevanceSerializer,
    PerceptionFurtherStudiesSerializer, FeedbackRecommendationsSerializer
)


# Address Views
class AddressListCreateView(ListCreateAPIView):
    """List and create addresses for the authenticated user"""
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AddressDetailView(RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a specific address"""
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


# Skills Relevance Views
class SkillsRelevanceView(APIView):
    """Get or create/update skills relevance for the authenticated user"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            skills_relevance = SkillsRelevance.objects.get(user=request.user)
            serializer = SkillsRelevanceSerializer(skills_relevance)
            return Response(serializer.data)
        except SkillsRelevance.DoesNotExist:
            return Response({'detail': 'Skills relevance not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request):
        skills_relevance, created = SkillsRelevance.objects.get_or_create(user=request.user)
        serializer = SkillsRelevanceSerializer(skills_relevance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        try:
            skills_relevance = SkillsRelevance.objects.get(user=request.user)
            serializer = SkillsRelevanceSerializer(skills_relevance, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except SkillsRelevance.DoesNotExist:
            return Response({'detail': 'Skills relevance not found'}, status=status.HTTP_404_NOT_FOUND)


# Curriculum Relevance Views
class CurriculumRelevanceView(APIView):
    """Get or create/update curriculum relevance for the authenticated user"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            curriculum_relevance = CurriculumRelevance.objects.get(user=request.user)
            serializer = CurriculumRelevanceSerializer(curriculum_relevance)
            return Response(serializer.data)
        except CurriculumRelevance.DoesNotExist:
            return Response({'detail': 'Curriculum relevance not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request):
        curriculum_relevance, created = CurriculumRelevance.objects.get_or_create(user=request.user)
        serializer = CurriculumRelevanceSerializer(curriculum_relevance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        try:
            curriculum_relevance = CurriculumRelevance.objects.get(user=request.user)
            serializer = CurriculumRelevanceSerializer(curriculum_relevance, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except CurriculumRelevance.DoesNotExist:
            return Response({'detail': 'Curriculum relevance not found'}, status=status.HTTP_404_NOT_FOUND)


# Perception Further Studies Views
class PerceptionFurtherStudiesView(APIView):
    """Get or create/update perception further studies for the authenticated user"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            perception_studies = PerceptionFurtherStudies.objects.get(user=request.user)
            serializer = PerceptionFurtherStudiesSerializer(perception_studies)
            return Response(serializer.data)
        except PerceptionFurtherStudies.DoesNotExist:
            return Response({'detail': 'Perception further studies not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request):
        perception_studies, created = PerceptionFurtherStudies.objects.get_or_create(user=request.user)
        serializer = PerceptionFurtherStudiesSerializer(perception_studies, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        try:
            perception_studies = PerceptionFurtherStudies.objects.get(user=request.user)
            serializer = PerceptionFurtherStudiesSerializer(perception_studies, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except PerceptionFurtherStudies.DoesNotExist:
            return Response({'detail': 'Perception further studies not found'}, status=status.HTTP_404_NOT_FOUND)


# Feedback Recommendations Views
class FeedbackRecommendationsView(APIView):
    """Get or create/update feedback recommendations for the authenticated user"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            feedback = FeedbackRecommendations.objects.get(user=request.user)
            serializer = FeedbackRecommendationsSerializer(feedback)
            return Response(serializer.data)
        except FeedbackRecommendations.DoesNotExist:
            return Response({'detail': 'Feedback recommendations not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request):
        feedback, created = FeedbackRecommendations.objects.get_or_create(user=request.user)
        serializer = FeedbackRecommendationsSerializer(feedback, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        try:
            feedback = FeedbackRecommendations.objects.get(user=request.user)
            serializer = FeedbackRecommendationsSerializer(feedback, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except FeedbackRecommendations.DoesNotExist:
            return Response({'detail': 'Feedback recommendations not found'}, status=status.HTTP_404_NOT_FOUND)
