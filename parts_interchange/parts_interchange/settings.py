"""
Django settings for parts_interchange project - Updated for Render deployment with PERFORMANCE OPTIMIZATIONS
"""

from pathlib import Path
import os
from decouple import config
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-your-secret-key-here-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=lambda v: [s.strip() for s in v.split(',')])

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'corsheaders',
    'django_filters',
]

LOCAL_APPS = [
    'apps.parts',
    'apps.vehicles',
    'apps.fitments',
    'apps.api',
    'apps.ebay_notifications',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # For static files on Render
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'parts_interchange.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'parts_interchange.wsgi.application'

# Database - Updated for Render PostgreSQL with SIMPLIFIED PERFORMANCE OPTIMIZATION
# Priority: DATABASE_URL > individual env vars > local development
if config('DATABASE_URL', default=None):
    # Production/Render - use DATABASE_URL with performance settings
    DATABASES = {
        'default': dj_database_url.config(
            default=config('DATABASE_URL'),
            conn_max_age=300,  # Keep connections alive for 5 minutes
            conn_health_checks=True,
        )
    }
    
    # Add safe PostgreSQL performance options
    DATABASES['default'].setdefault('OPTIONS', {})
    DATABASES['default']['OPTIONS'].update({
        'sslmode': 'prefer',
        'connect_timeout': 10,
        'application_name': 'parts_interchange',
    })
else:
    # Development - use individual environment variables
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME', default='parts_interchange_db'),
            'USER': config('DB_USER', default='postgres'),
            'PASSWORD': config('DB_PASSWORD', default='your_password_here'),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
            'CONN_MAX_AGE': 300,  # Keep connections alive
            'OPTIONS': {
                'sslmode': 'prefer',
                'connect_timeout': 10,
            },
        }
    }

# CACHING CONFIGURATION - Key performance improvement!
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'parts-interchange-cache',
        'TIMEOUT': 300,  # 5 minutes default
        'OPTIONS': {
            'MAX_ENTRIES': 2000,  # Increased cache size
            'CULL_FREQUENCY': 3,
        }
    }
}

# Session optimization - use cached sessions for better performance
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 1209600  # 2 weeks

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Whitenoise configuration for serving static files on Render
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework configuration - PERFORMANCE OPTIMIZED
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # Changed for better performance on public APIs
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 25,  # Reduced from 50 for better performance
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',  # Reduced from 200 for stability
        'user': '500/hour'   # Reduced from 1000 for stability
    },
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_METADATA_CLASS': None,  # Disable metadata for performance
    'COMPACT_JSON': True,  # Reduce response size
}

# CORS settings for API access
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://127.0.0.1:3000',
    cast=lambda v: [s.strip() for s in v.split(',')]
)

# CORS optimization
CORS_ALLOW_CREDENTIALS = True
CORS_PREFLIGHT_MAX_AGE = 86400  # 24 hours

# Security settings for production
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_REDIRECT_EXEMPT = []
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# PERFORMANCE SETTINGS
# Admin optimization
DATA_UPLOAD_MAX_NUMBER_FIELDS = 5000  # Reduced from default
ADMIN_MEDIA_PREFIX = '/static/admin/'

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB

# Email settings (for error reporting)
if not DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@partsinterchange.com')

# LOGGING CONFIGURATION - Respects LOG_LEVEL environment variable
LOG_LEVEL = config('LOG_LEVEL', default='WARNING' if not DEBUG else 'INFO')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'minimal': {
            'format': '{message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'minimal' if LOG_LEVEL in ['WARNING', 'ERROR', 'CRITICAL'] else 'simple',
            'level': LOG_LEVEL,
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
            'level': 'INFO',  # Always log INFO+ to file
        } if (BASE_DIR / 'logs').exists() else {
            'class': 'logging.NullHandler',  # Disable file logging if logs dir doesn't exist
        },
    },
    'root': {
        'level': LOG_LEVEL,
        'handlers': ['console'],
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'] if LOG_LEVEL == 'DEBUG' else [],
            'level': 'WARNING',  # Only show DB warnings/errors unless DEBUG
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',  # Only show request errors
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        # Silence noisy third-party packages
        'urllib3': {
            'level': 'WARNING',
            'propagate': False,
        },
        'requests': {
            'level': 'WARNING',
            'propagate': False,
        },
        'boto3': {
            'level': 'WARNING',
            'propagate': False,
        },
        'botocore': {
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# Custom settings for parts interchange - OPTIMIZED FOR LIVE DATA ENTRY
PARTS_INTERCHANGE = {
    'DEFAULT_MANUFACTURER': 'GM',
    'ENABLE_BULK_IMPORT': True,
    'CACHE_FITMENT_QUERIES': True,
    'ENABLE_QUERY_CACHE': True,
    'ADMIN_PAGE_SIZE': 10,  # Reduced to 10 for faster loading
    'API_PAGE_SIZE': 15,    # Reduced for faster API responses
    'MAX_SEARCH_RESULTS': 25,  # Reduced from 50
    'CACHE_TIMEOUT_SHORT': 600,   # 10 minutes (increased for live use)
    'CACHE_TIMEOUT_MEDIUM': 1800,  # 30 minutes
    'CACHE_TIMEOUT_LONG': 7200,   # 2 hours
    'DB_QUERY_TIMEOUT': 15,       # 15 seconds max query time (reduced)
    'ADMIN_LIST_PER_PAGE': 10,    # Smaller pages for faster loading
}

# Silence system check warnings and info messages
SILENCED_SYSTEM_CHECKS = [
    # Silence common development warnings that clutter output
    'security.W004',  # SECURE_HSTS_SECONDS warning
    'security.W008',  # SECURE_SSL_REDIRECT warning
    'security.W012',  # SESSION_COOKIE_SECURE warning
    'security.W016',  # CSRF_COOKIE_SECURE warning
    'security.W018',  # DEBUG=True warning
    'security.W019',  # ALLOWED_HOSTS warning for DEBUG=True
]

# Additional logging silence for clean output
if LOG_LEVEL in ['WARNING', 'ERROR', 'CRITICAL']:
    import warnings
    warnings.filterwarnings('ignore', category=DeprecationWarning)
    warnings.filterwarnings('ignore', category=PendingDeprecationWarning)
    warnings.filterwarnings('ignore', category=RuntimeWarning)

# Development settings
if DEBUG:
    # Add debug toolbar only in development and if LOG_LEVEL is DEBUG
    try:
        if LOG_LEVEL == 'DEBUG':
            import debug_toolbar
            INSTALLED_APPS += ['debug_toolbar']
            MIDDLEWARE.insert(1, 'debug_toolbar.middleware.DebugToolbarMiddleware')
            INTERNAL_IPS = ['127.0.0.1', 'localhost']
            
            # Debug toolbar configuration
            DEBUG_TOOLBAR_CONFIG = {
                'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG and LOG_LEVEL == 'DEBUG',
                'HIDE_DJANGO_SQL': False,
                'SHOW_TEMPLATE_CONTEXT': True,
            }
            
            # Show all SQL queries only if LOG_LEVEL is DEBUG
            LOGGING['loggers']['django.db.backends']['level'] = 'DEBUG'
            LOGGING['loggers']['django.db.backends']['handlers'] = ['console']
        
    except ImportError:
        pass  # Debug toolbar not installed
else:
    # Production optimizations
    # Disable admin documentation
    ADMIN_MEDIA_PREFIX = None
    
    # Security headers
    SECURE_REFERRER_POLICY = 'same-origin'
    SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'

# Database query optimization
if 'postgresql' in DATABASES['default']['ENGINE']:
    # PostgreSQL specific optimizations
    DATABASES['default'].setdefault('OPTIONS', {})
    DATABASES['default']['OPTIONS'].update({
        'sslmode': 'prefer' if DEBUG else 'require',
    })
