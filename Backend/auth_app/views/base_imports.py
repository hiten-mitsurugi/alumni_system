# Common imports shared across all view modules
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.generics import ListAPIView, RetrieveAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.cache import cache
from django.db.models import Q
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction
from django.utils import timezone
import pandas as pd
import io
from datetime import datetime
import logging
from django.contrib.auth import get_user_model
from rest_framework import viewsets
import os
import uuid

# Local imports - use auth_app prefix for absolute imports
from auth_app.models import (
    CustomUser, Skill, WorkHistory, AlumniDirectory, Profile, Address, 
    SkillsRelevance, CurriculumRelevance, PerceptionFurtherStudies, 
    FeedbackRecommendations, UserSkill, Following
)
from auth_app.status_cache import set_user_online, set_user_offline, get_user_status
from auth_app.serializers import (
    RegisterSerializer, UserDetailSerializer, UserCreateSerializer,
    SkillSerializer, WorkHistorySerializer, AlumniDirectoryCheckSerializer,
    ProfileSerializer, UserSearchSerializer, AlumniDirectorySerializer,
    AddressSerializer, EnhancedUserDetailSerializer, UserSkillSerializer
)
from auth_app.permissions import IsAdminOrSuperAdmin
from auth_app.utils import generate_token, confirm_token
from auth_app.email_templates.approval_email import get_approval_email_template, get_rejection_email_template
from django.urls import reverse

logger = logging.getLogger(__name__)
