from pathlib import Path
import os
import random
import string

# ================================
# PATHS
# ================================
BASE_DIR = Path(__file__).resolve().parent.parent

# ================================
# SECURITY
# ================================
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-dev-key")

DEBUG = os.getenv("DEBUG", "False") == "True"

# Render app hostname
RENDER_HOSTNAME = "chatsupport-ruq6.onrender.com"

ALLOWED_HOSTS = [
    RENDER_HOSTNAME,
    "localhost",
    "127.0.0.1",
]

# CSRF trusted origins (for HTTPS)
CSRF_TRUSTED_ORIGINS = [
    f"https://{RENDER_HOSTNAME}"
]

# ================================
# APPLICATIONS
# ================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party apps
    'corsheaders',
    'rest_framework',
    'ipware',

    # Your apps
    'chat',
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",        # ✅ must be first
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",   # Serve static files
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = 'support_chat.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'chat' / 'templates'],
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

WSGI_APPLICATION = 'support_chat.wsgi.application'
# If using WebSockets later → uncomment this
# ASGI_APPLICATION = 'support_chat.asgi.application'

# ================================
# DATABASE (Render PostgreSQL)
# ================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mychatdb_obts',
        'USER': 'mychatdb_obts_user',
        'PASSWORD': 'bnBzkF0ObG5PZf34PecHIwpuU4k6WqGq',
        'HOST': 'dpg-d3ds5eodl3ps73c5ijng-a.render.com',
        'PORT': '5432',
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}

# ================================
# PASSWORD VALIDATION
# ================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ================================
# INTERNATIONALIZATION
# ================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ================================
# STATIC FILES (Whitenoise)
# ================================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ================================
# CORS Settings
# ================================
CORS_ALLOWED_ORIGINS = [
    f"https://{RENDER_HOSTNAME}",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]

# ================================
# Iframe + Cookie Settings
# ================================
# ✅ Allow iframe embedding
X_FRAME_OPTIONS = "ALLOWALL"

# ✅ Cookies for iframe (important for sessions inside iframe)
SESSION_COOKIE_SAMESITE = "None"
SESSION_COOKIE_SECURE = not DEBUG  # HTTPS required in production

CSRF_COOKIE_SAMESITE = "None"
CSRF_COOKIE_SECURE = not DEBUG

# ================================
# DEFAULT PRIMARY KEY
# ================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ================================
# SERVER RUN ID (optional)
# ================================
SERVER_RUN_ID = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
