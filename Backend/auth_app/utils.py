import uuid
from django.core.cache import cache
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from django.conf import settings
from django.http import HttpRequest


# ----------------------
# UUID Token with Caching (e.g. approval link)
# ----------------------

def generate_uuid_token(user) -> str:
    """
    Generate a short-lived UUID token and store user's email in cache.
    Good for approval workflows.
    """
    token = str(uuid.uuid4())
    cache.set(f'confirm_token_{token}', user.email, timeout=3600)  # Cache for 1 hour
    return token


def confirm_uuid_token(token: str) -> str | None:
    """
    Confirm UUID token from cache and return email.
    """
    return cache.get(f'confirm_token_{token}')


# ----------------------
# Time-sensitive Signed Token (e.g. email confirmation)
# ----------------------

def generate_token(user) -> str:
    """
    Generate a time-sensitive signed token using the user's email.
    """
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    return serializer.dumps(user.email)


def confirm_token(token: str, expiration: int = 3600) -> str | None:
    """
    Confirm a signed token and return email if valid.
    """
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    try:
        return serializer.loads(token, max_age=expiration)
    except (SignatureExpired, BadSignature):
        return None


# ----------------------
# Lockout Hook for django-axes (optional)
# ----------------------

def my_lockout_function(request: HttpRequest, credentials: dict) -> bool:
    """
    Dummy lockout function for django-axes.
    """
    return True
