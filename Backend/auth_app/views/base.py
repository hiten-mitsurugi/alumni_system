# Shared imports and base configurations for auth_app views
import csv
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.generics import ListAPIView, RetrieveAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.cache import cache
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction
from django.utils import timezone
import pandas as pd
import io
from datetime import datetime
import logging

# Local imports
from ..models import CustomUser, Skill, WorkHistory, AlumniDirectory, Profile

# Import additional models that may exist
try:
    from ..models import Follow
except ImportError:
    Follow = None
from ..status_cache import set_user_online, set_user_offline, get_user_status
from ..serializers import (
    RegisterSerializer, UserDetailSerializer, UserCreateSerializer,
    SkillSerializer, WorkHistorySerializer, AlumniDirectoryCheckSerializer,
    ProfileSerializer, UserSearchSerializer, AlumniDirectorySerializer
)
from ..permissions import IsAdminOrSuperAdmin
from ..utils import generate_token, confirm_token
from ..email_templates.approval_email import get_approval_email_template, get_rejection_email_template
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import viewsets

# Configure logger
logger = logging.getLogger(__name__)