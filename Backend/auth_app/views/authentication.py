"""
Authentication related views - Login, Register, Logout, Email confirmation
"""
from .base_imports import *

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        import json
        
        # Add detailed logging for debugging
        logger.info("=== REGISTRATION ATTEMPT ===")
        logger.info(f"Request data keys: {list(request.data.keys())}")
        logger.info(f"Alumni exists value: {request.data.get('alumni_exists')}")
        logger.info(f"Survey responses: {request.data.get('survey_responses')}")
        logger.info(f"Email: {request.data.get('email')}")
        logger.info(f"Employment status: {request.data.get('employment_status')}")
        logger.info(f"Gender: {request.data.get('gender')}")
        logger.info(f"Civil status: {request.data.get('civil_status')}")
        
        # Parse JSON fields from FormData - avoid deep copy to prevent pickle issues
        data = {}
        
        # Copy non-file fields
        for key, value in request.data.items():
            if key not in ['government_id', 'profile_picture']:
                data[key] = value
        
        # Handle file fields separately (don't copy, just reference)
        if 'government_id' in request.data:
            data['government_id'] = request.data['government_id']
        if 'profile_picture' in request.data:
            data['profile_picture'] = request.data['profile_picture']
        
        # Parse address data if present
        if 'present_address_data' in data and isinstance(data['present_address_data'], str):
            try:
                data['present_address_data'] = json.loads(data['present_address_data'])
                logger.info(f"Parsed present_address_data: {data['present_address_data']}")
            except json.JSONDecodeError:
                logger.error("Failed to parse present_address_data JSON")
                
        if 'permanent_address_data' in data and isinstance(data['permanent_address_data'], str):
            try:
                data['permanent_address_data'] = json.loads(data['permanent_address_data'])
                logger.info(f"Parsed permanent_address_data: {data['permanent_address_data']}")
            except json.JSONDecodeError:
                logger.error("Failed to parse permanent_address_data JSON")
        
        serializer = RegisterSerializer(data=data)

        if serializer.is_valid():
            try:
                with transaction.atomic():
                    user = serializer.save()
                    logger.info(f"User created successfully: {user.email}")

                    try:
                        channel_layer = get_channel_layer()
                        async_to_sync(channel_layer.group_send)(
                            'admin_notifications',
                            {
                                'type': 'send_notification',
                                'message': {
                                    'type': 'new_user',
                                    'user_id': user.id,
                                    'email': user.email,
                                    'first_name': user.first_name,
                                    'last_name': user.last_name
                                }
                            }
                        )
                    except Exception as ws_error:
                        logger.error(f"WebSocket notification failed in RegisterView: {str(ws_error)}")

                return Response(
                    {'message': 'User registered successfully, pending approval.'},
                    status=status.HTTP_201_CREATED
                )

            except Exception as db_error:
                logger.error(f"Database error during registration: {str(db_error)}")
                return Response(
                    {'error': 'An error occurred while processing your registration.'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        # Log validation errors for debugging
        logger.error("=== REGISTRATION VALIDATION FAILED ===")
        logger.error(f"Serializer errors: {serializer.errors}")
        for field, errors in serializer.errors.items():
            logger.error(f"Field '{field}': {errors}")
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        logger.info(f"🔍 Login attempt - Email: {email}")
        
        if not email or not password:
            return Response({'detail': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # First find user by email
            user = CustomUser.objects.filter(email=email).first()
            if user is None:
                logger.info(f"❌ No user found with email: {email}")
                return Response({'detail': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
            
            logger.info(f"✅ User found: {user.username} (ID: {user.id})")
            
            # Authenticate using username, not email - this is important for AXES tracking
            authenticated_user = authenticate(request=request, username=user.username, password=password)
            logger.info(f"🔐 Authentication result: {authenticated_user}")
            
            if authenticated_user is None:
                return Response({'detail': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
            
            # Check if user needs approval (alumni users)
            if not user.is_approved and user.user_type == 3:
                return Response(
                    {'detail': 'Not yet approved, please contact the Alumni Relations Office'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Check if user is blocked
            if not user.is_active:
                return Response(
                    {'detail': 'Your account has been blocked. Please contact the administrator.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Generate tokens FIRST (fastest operation)
            refresh = RefreshToken.for_user(user)
            
            # Update user's last_login field and status (do this in background)
            from threading import Thread
            def update_login_status():
                try:
                    user.last_login = timezone.now()
                    user.save(update_fields=['last_login'])
                    set_user_online(user.id)
                    
                    # Update profile status
                    try:
                        from auth_app.models import Profile
                        profile, created = Profile.objects.get_or_create(user=user)
                        profile.status = 'online'
                        profile.last_seen = timezone.now()
                        profile.save()
                        logger.info(f"User {user.id} status set to online on login")
                    except Exception as profile_error:
                        logger.error(f"Profile update failed: {str(profile_error)}")
                    
                    # Broadcast status change to all connected users
                    try:
                        channel_layer = get_channel_layer()
                        status_payload = {
                            'type': 'status_update',
                            'user_id': user.id,
                            'status': 'online',
                            'last_seen': timezone.now().isoformat(),
                            'last_login': user.last_login.isoformat()
                        }
                        async_to_sync(channel_layer.group_send)(
                            'status_updates',
                            {
                                'type': 'status_update',
                                'data': status_payload
                            }
                        )
                        logger.info(f"Successfully broadcast login status update for user {user.id}")
                    except Exception as ws_error:
                        logger.error(f"WebSocket status broadcast failed in LoginView: {str(ws_error)}")
                except Exception as e:
                    logger.error(f"Background login status update failed: {str(e)}")
            
            # Run status update in background thread (non-blocking)
            background_thread = Thread(target=update_login_status, daemon=True)
            background_thread.start()
            
            return Response({
                'token': str(refresh.access_token),
                'user': UserDetailSerializer(user).data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Login failed for email {email}: {str(e)}", exc_info=True)
            return Response({'detail': 'An error occurred during login.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Update user's online status in profile
            user = request.user
            if hasattr(user, 'profile') and user.profile:
                user.profile.status = 'offline'
                user.profile.last_seen = timezone.now()
                user.profile.save(update_fields=['status', 'last_seen'])
            
            # Update status cache
            set_user_offline(user.id)
            
            # Send status update notification
            try:
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'user_{user.id}',
                    {
                        'type': 'status_update',
                        'message': {
                            'user_id': user.id,
                            'status': 'offline',
                            'last_seen': timezone.now().isoformat()
                        }
                    }
                )
            except Exception as ws_error:
                logger.error(f"WebSocket status update failed in LogoutView: {str(ws_error)}")

            # Blacklist the refresh token
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                try:
                    token = RefreshToken(refresh_token)
                    token.blacklist()
                except Exception as token_error:
                    logger.error(f"Token blacklisting failed: {str(token_error)}")

            return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return Response({'error': 'Logout failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConfirmTokenView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        email = cache.get(f'confirm_token_{token}')
        if not email:
            email = confirm_token(token)
        if email:
            try:
                user = CustomUser.objects.get(email=email)
                if user.is_approved:
                    refresh = RefreshToken.for_user(user)
                    cache.delete(f'confirm_token_{token}')
                    return Response({
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'user_type': user.user_type,
                    })
                return Response({'error': 'Account not approved'}, status=status.HTTP_403_FORBIDDEN)
            except CustomUser.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)


class CheckEmailExistsView(APIView):
    """Public endpoint to check if an email is already registered - for use during registration"""
    permission_classes = [AllowAny]  # No authentication required
    
    def get(self, request):
        email = request.query_params.get('email', '').strip()
        
        if not email:
            return Response({'error': 'Email parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            # Check if email already exists
            user_exists = CustomUser.objects.filter(email__iexact=email).exists()
            
            return Response({
                'exists': user_exists,
                'email': email,
                'message': 'Email is already registered' if user_exists else 'Email is available'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error checking email existence for {email}: {str(e)}")
            return Response({'error': 'Unable to check email availability'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ForgotPasswordView(APIView):
    """
    Handle forgot password requests.
    Validates email exists in system and sends random password to registered email.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        import re
        import secrets
        import string
        
        email = request.data.get('email', '').strip()
        
        # Validate email format using regex
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not email or not re.match(email_regex, email):
            logger.warning(f"Invalid email format provided: {email}")
            return Response(
                {'detail': 'Please enter a valid email address'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Check if email exists in CustomUser
            user = CustomUser.objects.filter(email=email).first()
            
            if not user:
                logger.warning(f"Password reset requested for non-existent email: {email}")
                # Return same error message for security (don't reveal if email exists)
                return Response(
                    {'detail': 'If an account exists with this email, you will receive a password reset email.'},
                    status=status.HTTP_200_OK
                )
            
            # Generate random password (12 characters: uppercase, lowercase, digits, special chars)
            characters = string.ascii_letters + string.digits + string.punctuation
            random_password = ''.join(secrets.choice(characters) for _ in range(12))
            
            # Update user's password
            user.set_password(random_password)
            user.save()
            logger.info(f"Password reset for user: {user.email} (ID: {user.id})")
            
            # Send email in background thread (non-blocking)
            from threading import Thread
            def send_reset_email():
                try:
                    subject = 'Alumni Mates - Password Reset'
                    plain_message = f"""
Hello {user.first_name},

A password reset request was submitted for your Alumni Mates account.

Your temporary password is: {random_password}

Please use this password to log in to your account. You can change it to a more secure password after logging in.

If you did not request this password reset, please contact our support team immediately.

Best regards,
Alumni Mates Support Team
                    """
                    
                    html_message = f"""
<html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9;">
            <div style="background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h2 style="color: #ff6600;">Password Reset Request</h2>
                
                <p>Hello <strong>{user.first_name}</strong>,</p>
                
                <p>A password reset request was submitted for your Alumni Mates account.</p>
                
                <div style="background-color: #f0f0f0; padding: 15px; border-left: 4px solid #ff6600; margin: 20px 0;">
                    <p style="margin: 0;"><strong>Your temporary password is:</strong></p>
                    <p style="margin: 10px 0; font-size: 18px; font-weight: bold; color: #ff6600; font-family: monospace;">{random_password}</p>
                </div>
                
                <p>Please use this password to log in to your account. <strong>You can change it to a more secure password after logging in.</strong></p>
                
                <p style="color: #666; font-size: 14px; border-top: 1px solid #ddd; padding-top: 15px; margin-top: 20px;">
                    If you did not request this password reset, please contact our support team immediately at <strong>support@alumnimates.com</strong>
                </p>
                
                <p style="color: #999; font-size: 12px; margin-top: 20px;">
                    Best regards,<br>
                    <strong>Alumni Mates Support Team</strong>
                </p>
            </div>
        </div>
    </body>
</html>
                    """
                    
                    email_obj = EmailMultiAlternatives(
                        subject=subject,
                        body=plain_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[user.email]
                    )
                    email_obj.attach_alternative(html_message, "text/html")
                    email_obj.send(fail_silently=False)
                    logger.info(f"Password reset email sent successfully to {user.email}")
                except Exception as email_error:
                    logger.error(f"Failed to send password reset email to {user.email}: {str(email_error)}")
            
            email_thread = Thread(target=send_reset_email, daemon=True)
            email_thread.start()
            
            return Response(
                {'detail': 'If an account exists with this email, you will receive a password reset email.'},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Unexpected error in ForgotPasswordView: {str(e)}", exc_info=True)
            return Response(
                {'detail': 'An error occurred processing your request. Please try again later.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
