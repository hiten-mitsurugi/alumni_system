"""
Survey App - Admin Management Views
===================================
Views for admin-only survey management operations including:
- Category management (CRUD)
- Question management (CRUD)
- Form/Template management (CRUD)
- Response viewing and analytics
"""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count
from django.utils import timezone
from django.core.cache import cache
from django.shortcuts import get_object_or_404

from ..models import SurveyCategory, SurveyQuestion, SurveyResponse, SurveyTemplate
from ..serializers import (
    SurveyCategorySerializer,
    SurveyQuestionSerializer,
    SurveyResponseDetailSerializer,
    SurveyTemplateSerializer
)
from ..permissions import IsSurveyAdmin, IsSuperAdminOnly


# =============================================================================
# CATEGORY MANAGEMENT
# =============================================================================

class SurveyCategoryListCreateView(generics.ListCreateAPIView):
    """
    List all survey categories or create a new one.
    Only admins can access this endpoint.
    """
    serializer_class = SurveyCategorySerializer
    permission_classes = [IsSurveyAdmin]
    
    def get_queryset(self):
        return SurveyCategory.objects.all().order_by('order', 'name')
    
    def perform_create(self, serializer):
        """Save category with audit information"""
        super().perform_create(serializer)


class SurveyCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a survey category.
    Only super admins can delete categories.
    """
    serializer_class = SurveyCategorySerializer
    queryset = SurveyCategory.objects.all()
    
    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsSuperAdminOnly()]
        return [IsSurveyAdmin()]
    
    def perform_update(self, serializer):
        """Update category"""
        super().perform_update(serializer)
    
    def perform_destroy(self, instance):
        """Delete category"""
        super().perform_destroy(instance)


# =============================================================================
# QUESTION MANAGEMENT
# =============================================================================

class SurveyQuestionListCreateView(generics.ListCreateAPIView):
    """
    List all survey questions or create a new one.
    Supports filtering by category and active status.
    """
    serializer_class = SurveyQuestionSerializer
    permission_classes = [IsSurveyAdmin]
    
    def get_queryset(self):
        queryset = SurveyQuestion.objects.select_related('category', 'created_by')
        
        # Filter by category
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('category__order', 'order', 'question_text')
    
    def perform_create(self, serializer):
        """Save question with audit information"""
        super().perform_create(serializer)


class SurveyQuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a survey question.
    Only super admins can delete questions.
    """
    serializer_class = SurveyQuestionSerializer
    queryset = SurveyQuestion.objects.all()
    
    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsSuperAdminOnly()]
        return [IsSurveyAdmin()]
    
    def perform_update(self, serializer):
        """Update question"""
        super().perform_update(serializer)
    
    def perform_destroy(self, instance):
        """Delete question"""
        super().perform_destroy(instance)


# =============================================================================
# FORM/TEMPLATE MANAGEMENT
# =============================================================================

class SurveyFormListCreateView(generics.ListCreateAPIView):
    """
    List all forms (templates) or create a new form.
    Uses SurveyTemplate as the Form model.
    """
    serializer_class = SurveyTemplateSerializer
    permission_classes = [IsSurveyAdmin]

    def get_queryset(self):
        return SurveyTemplate.objects.all().order_by('name')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class SurveyFormDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a form/template."""
    serializer_class = SurveyTemplateSerializer
    queryset = SurveyTemplate.objects.all()

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsSuperAdminOnly()]
        return [IsSurveyAdmin()]

    def retrieve(self, request, *args, **kwargs):
        """Return nested form -> categories -> questions structure"""
        instance = self.get_object()
        form_data = SurveyTemplateSerializer(instance).data

        # Attach categories with their questions
        # FIX: Use SurveyTemplateCategory order, not SurveyCategory order
        template_categories = instance.surveytemplatecategory_set.all().select_related('category').order_by('order')
        categories_data = []
        for tc in template_categories:
            cat = tc.category
            questions = SurveyQuestion.objects.filter(category=cat).order_by('order', 'question_text')
            qdata = SurveyQuestionSerializer(questions, many=True).data
            categories_data.append({
                'category': SurveyCategorySerializer(cat).data,
                'questions': qdata
            })

        form_data['sections'] = categories_data
        return Response(form_data)

    def perform_update(self, serializer):
        """
        Allow updating template fields and categories.
        Auto-generate public_slug when share_enabled is toggled to True.
        """
        instance = serializer.instance
        share_enabled = serializer.validated_data.get('share_enabled', instance.share_enabled)
        
        # Auto-generate slug if share_enabled is True and slug doesn't exist
        if share_enabled and not instance.public_slug:
            from ..utils import generate_unique_survey_slug
            instance.public_slug = generate_unique_survey_slug(instance.name)
        
        # If share_enabled is being disabled, optionally clear the slug (or keep it)
        # For now, we'll keep the slug even if sharing is disabled
        # This allows re-enabling without changing the URL
        
        serializer.save()


class SurveyFormPublishView(APIView):
    """Toggle publish or accepting responses for a form."""
    permission_classes = [IsSurveyAdmin]

    def post(self, request, pk):
        form = get_object_or_404(SurveyTemplate, pk=pk)
        is_published = request.data.get('is_published')
        accepting = request.data.get('accepting_responses')

        if is_published is not None:
            form.is_published = bool(is_published)
        if accepting is not None:
            form.accepting_responses = bool(accepting)
        form.save()

        return Response({
            'message': 'Form updated',
            'is_published': form.is_published,
            'accepting_responses': form.accepting_responses
        })


# =============================================================================
# RESPONSE VIEWING
# =============================================================================

class SurveyResponsesView(generics.ListAPIView):
    """
    List all survey responses for admin review.
    Supports filtering by user, question, and category.
    """
    serializer_class = SurveyResponseDetailSerializer
    permission_classes = [IsSurveyAdmin]
    
    def get_queryset(self):
        queryset = SurveyResponse.objects.select_related(
            'user', 'question', 'question__category'
        )
        
        # Filter by user
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by question
        question_id = self.request.query_params.get('question_id')
        if question_id:
            queryset = queryset.filter(question_id=question_id)
        
        # Filter by category (single)
        category_id = self.request.query_params.get('category_id')
        if category_id:
            queryset = queryset.filter(question__category_id=category_id)
        
        # Filter by multiple categories
        category_ids = self.request.query_params.get('category_ids')
        if category_ids:
            try:
                # Handle both comma-separated string and array
                if isinstance(category_ids, str):
                    ids = [int(id.strip()) for id in category_ids.split(',') if id.strip()]
                else:
                    ids = category_ids
                queryset = queryset.filter(question__category_id__in=ids)
            except (ValueError, TypeError):
                pass
        
        # Filter by programs
        programs = self.request.query_params.get('programs')
        if programs:
            program_list = [p.strip() for p in programs.split(',') if p.strip()]
            if program_list:
                queryset = queryset.filter(user__program__in=program_list)
        
        # Filter by graduation years
        graduation_years = self.request.query_params.get('graduation_years')
        if graduation_years:
            try:
                year_list = [int(y.strip()) for y in graduation_years.split(',') if y.strip()]
                if year_list:
                    queryset = queryset.filter(user__year_graduated__in=year_list)
            except (ValueError, TypeError):
                pass
        
        return queryset.order_by('-submitted_at')
