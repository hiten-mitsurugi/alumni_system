
import os
from pathlib import Path
from datetime import timedelta
from decouple import config
import environ

BASE_DIR = Path(__file__).resolve().parent.parent
# Load environment variables from Backend/.env (always use the correct one)
env = environ.Env()
environ.Env.read_env(env_file=os.path.join(BASE_DIR, '.env'))

# === Core Settings ===
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = ['*']

# === Installed Apps ===
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_cryptography',
    'django_extensions',
    'rest_framework',
    'rest_framework_simplejwt',
    'channels',
    'corsheaders',
    'axes',
    'auth_app',
    'posts_app',
    'messaging_app',
    'survey_app',  # NEW - Dynamic Survey System
]

# === Middleware ===
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',
]

# === URL Configuration ===
ROOT_URLCONF = 'alumni_system.urls'

# === Templates ===
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# === WSGI/ASGI ===
WSGI_APPLICATION = 'alumni_system.wsgi.application'
ASGI_APPLICATION = 'alumni_system.asgi.application'

# === Database ===
# Uncomment PostgreSQL config when ready
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}

# SQLite for local development (backup option)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# === Authentication & Authorization ===
AUTH_USER_MODEL = 'auth_app.CustomUser'
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
    {'NAME': 'auth_app.validators.CustomPasswordValidator'},
]

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# === Django REST Framework ===
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ]
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# === Email Settings ===
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')

# === Redis Settings ===
REDIS_HOST = config('REDIS_HOST', default='127.0.0.1')
REDIS_PORT = config('REDIS_PORT', default='6379')
REDIS_PASSWORD = config('REDIS_PASSWORD', default='')
REDIS_URL = config('REDIS_URL', default=f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/0')

# Test Redis connectivity function
def test_redis_connection():
    """Test if Redis is available"""
    try:
        import redis
        # Set a short timeout for development to avoid long waits
        r = redis.Redis(
            host=REDIS_HOST, 
            port=REDIS_PORT, 
            password=REDIS_PASSWORD if REDIS_PASSWORD else None, 
            db=0,
            socket_connect_timeout=2,  # 2 second timeout
            socket_timeout=2,
            retry_on_timeout=False
        )
        r.ping()
        return True
    except Exception as e:
        print(f"Redis not available: {e}")
        return False

# === Caching ===
# Configure caching based on Redis availability
if test_redis_connection():
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/1',
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }

# === Channels ===
# Configure channel layers based on Redis availability
if test_redis_connection():
    print("✅ Redis is available - using Redis channel layer")
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                'hosts': [f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/2'],
                'prefix': 'alumni_channels',
                'capacity': 1000,
                'expiry': 60,
            },
        },
    }
else:
    print("⚠️  Redis not available - using in-memory channel layer")
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer'
        }
    }

# === Django Cryptography ===
CRYPTOGRAPHY_BACKEND = 'django_cryptography.core.backends.default.DefaultBackend'
CRYPTOGRAPHY_SALT = config('CRYPTOGRAPHY_SALT', default='alumni_system_salt_2025')

# === Static & Media Files ===
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
frontend_static = os.path.join(BASE_DIR, 'static/frontend')
STATICFILES_DIRS = [frontend_static] if os.path.exists(frontend_static) else []
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# === Other Settings ===
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# === CORS Settings ===
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='http://localhost:8000,http://localhost:8080,http://localhost:5173', cast=lambda v: [s.strip() for s in v.split(',')])
CORS_ALLOW_ALL_ORIGINS = True
# === Axes (Brute-force protection) ===
AXES_ENABLED = True
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = timedelta(minutes=15)
AXES_RESET_ON_SUCCESS = True
AXES_USERNAME_FORM_FIELD = "email"
AXES_LOCKOUT_CALLABLE = 'auth_app.utils.my_lockout_function'

# === Logging ===
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# === Survey System Configuration ===
SURVEY_CONFIG = {
    'MODE': 'hybrid',  # Options: 'static', 'dynamic', 'hybrid'
    'ENABLE_DYNAMIC_ADMIN': True,  # Enable admin interface for survey management
    'PRESERVE_STATIC_DATA': True,  # Keep existing static survey data
    'AUTO_MIGRATE_RESPONSES': False,  # Automatic migration from static to dynamic
    'CACHE_TIMEOUT': 1800,  # Cache timeout for survey data (30 minutes)
    'MAX_QUESTIONS_PER_CATEGORY': 50,  # Limit questions per category
    'ENABLE_ANALYTICS': True,  # Enable survey analytics
}