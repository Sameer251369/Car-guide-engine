import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

# =========================================================
# SECURITY
# =========================================================

SECRET_KEY = os.environ.get('SECRET_KEY')

if not SECRET_KEY and os.environ.get('ENVIRONMENT') == 'production':
    raise ValueError(
        "SECRET_KEY environment variable must be set for production"
    )

if not SECRET_KEY:
    SECRET_KEY = 'django-insecure-car-guide-media-kaarbear-key-2026'

IS_PRODUCTION = (
    os.environ.get('ENVIRONMENT', 'development') == 'production'
)

DEBUG = os.environ.get(
    'DEBUG', 'False' if IS_PRODUCTION else 'True'
).lower() == 'true'

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get(
        'ALLOWED_HOSTS', 'localhost,127.0.0.1,[::1]'
    ).split(',')
    if host.strip()
]

# Keep both Render backend hostnames supported.
RENDER_HOSTS = [
    'car-guide-engine-hp7p.onrender.com',
    'car-guide-engine.onrender.com',
]

for host in RENDER_HOSTS:
    if host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(host)

RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')

if RENDER_EXTERNAL_HOSTNAME and RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)


def _split_origins(value):
    return [
        origin.strip().rstrip('/')
        for origin in value.split(',')
        if origin.strip()
    ]


def _unique(items):
    return list(dict.fromkeys(items))


# =========================================================
# CORS AND CSRF
# =========================================================

FRONTEND_ORIGINS = _unique([
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:3001',
    'http://127.0.0.1:3001',
    'http://localhost:3002',
    'http://127.0.0.1:3002',
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'http://localhost:8000',
    'http://127.0.0.1:8000',

    # Existing frontend
    'https://car-guide-ext.vercel.app',

    # New backend
    'https://car-guide-engine-hp7p.onrender.com',

    # Previous backend (kept for compatibility)
    'https://car-guide-engine.onrender.com',

    *_split_origins(os.environ.get('CORS_ORIGINS', '')),
])

CSRF_TRUSTED_ORIGINS = _unique([
    *FRONTEND_ORIGINS,
    'https://*.vercel.app',
])

CORS_ALLOWED_ORIGINS = [
    origin for origin in FRONTEND_ORIGINS
    if '*' not in origin
]

CORS_ALLOWED_ORIGIN_REGEXES = [
    r'^https://[a-z0-9-]+\.vercel\.app$',
]

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True

# =========================================================
# SECURE COOKIES / RENDER
# =========================================================

IS_RENDER = bool(
    os.environ.get('RENDER')
    or os.environ.get('RENDER_EXTERNAL_HOSTNAME')
)

if IS_PRODUCTION or IS_RENDER:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SAMESITE = 'None'
    SESSION_COOKIE_SAMESITE = 'None'
    CSRF_COOKIE_HTTPONLY = False
else:
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SAMESITE = 'Lax'
    CSRF_COOKIE_HTTPONLY = False

# =========================================================
# APPLICATIONS
# =========================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'corsheaders',
    'django_filters',
    'cloudinary_storage',
    'cloudinary',

    'portfolio',
    'blog',
    'calculator',
    'leads',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'carguide.urls'

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

WSGI_APPLICATION = 'carguide.wsgi.application'

# =========================================================
# DATABASE
# =========================================================

def get_database_config():
    raw_url = os.environ.get('DATABASE_URL')

    if not raw_url or dj_database_url is None:
        if IS_PRODUCTION:
            raise ImproperlyConfigured(
                'Production requires DATABASE_URL and dj-database-url; '
                'refusing to use ephemeral SQLite.'
            )

        return {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }

    if isinstance(raw_url, bytes):
        raw_url = raw_url.decode('utf-8')

    raw_url = raw_url.strip()

    if not raw_url:
        if IS_PRODUCTION:
            raise ImproperlyConfigured(
                'Production DATABASE_URL cannot be empty.'
            )

        return {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }

    try:
        database_config = dj_database_url.parse(raw_url)

        if (
            IS_PRODUCTION
            and database_config.get('ENGINE')
            != 'django.db.backends.postgresql'
        ):
            raise ImproperlyConfigured(
                'Production DATABASE_URL must point to PostgreSQL.'
            )

        return database_config

    except ImproperlyConfigured:
        raise

    except Exception as exc:
        if IS_PRODUCTION:
            raise ImproperlyConfigured(
                'Production DATABASE_URL is invalid.'
            ) from exc

        return {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }


DATABASES = {
    'default': get_database_config()
}

# =========================================================
# PASSWORD VALIDATION
# =========================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'
    },
]

# =========================================================
# INTERNATIONALIZATION
# =========================================================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# =========================================================
# STATIC AND MEDIA FILES
# =========================================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# =========================================================
# CLOUDINARY
# =========================================================

CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME', '')
CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY', '')
CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET', '')

HAS_CLOUDINARY = bool(
    CLOUDINARY_CLOUD_NAME
    and CLOUDINARY_API_KEY
    and CLOUDINARY_API_SECRET
)

STORAGES = {
    'default': {
        'BACKEND': (
            'cloudinary_storage.storage.MediaCloudinaryStorage'
            if HAS_CLOUDINARY
            else 'django.core.files.storage.FileSystemStorage'
        ),
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

if HAS_CLOUDINARY:
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': CLOUDINARY_CLOUD_NAME,
        'API_KEY': CLOUDINARY_API_KEY,
        'API_SECRET': CLOUDINARY_API_SECRET,
    }

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =========================================================
# REST FRAMEWORK
# =========================================================

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '10000/hour',
        'user': '10000/hour',
        'leads': '100/hour',
        'estimate': '500/hour',
    },
}

