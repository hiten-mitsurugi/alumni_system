from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in using their email address.
    """
    
    def authenticate(self, request, username=None, password=None, email=None, **kwargs):
        print(f"EmailBackend.authenticate called with email={email}, username={username}")
        
        if email is None:
            email = username
        
        if not email:
            print("No email provided")
            return None
            
        try:
            user = User.objects.get(email=email)
            print(f"Found user: {user.username} for email: {email}")
        except User.DoesNotExist:
            print(f"No user found with email: {email}")
            return None
        
        if user.check_password(password):
            print(f"Password check passed for user: {user.username}")
            if self.user_can_authenticate(user):
                print(f"User can authenticate: {user.username}")
                return user
            else:
                print(f"User cannot authenticate (inactive?): {user.username}")
        else:
            print(f"Password check failed for user: {user.username}")
        
        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
