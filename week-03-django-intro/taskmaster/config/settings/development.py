"""
Development settings - For local development only.
"""

from .base import *

DEBUG = True

# Load secret key (with fallback for development)
SECRET_KEY = config("SECRET_KEY", default="django-insecure-dev-key-do-not-use-in-production")

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# SQLite for development
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Redis (optional - use if available, fallback to local memory)
try:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }
    CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://127.0.0.1:6379/0')
    CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://127.0.0.1:6379/0')
except ImportError:
    # Fallback to local memory cache if redis not installed
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }
    CELERY_BROKER_URL = 'memory://'
    CELERY_RESULT_BACKEND = 'cache'

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

CELERY_BEAT_SCHEDULE = {
    'cleanup-old-tasks': {
        'task': 'tasks.tasks.cleanup_old_tasks',
        'schedule': 86400.0,  # Daily
    },
}

# Email to console for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Debug tools (only in development)
INSTALLED_APPS += [
    "debug_toolbar",
    "silk",
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "silk.middleware.SilkyMiddleware",
] + MIDDLEWARE

INTERNAL_IPS = ["127.0.0.1"]

SILKY_PYTHON_PROFILER = True
SILKY_PYTHON_PROFILER_BINARY = True
SILKY_PYTHON_PROFILER_FUNC = None
SILKY_INTERCEPT_PERCENT = 100

# Logging for development
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}