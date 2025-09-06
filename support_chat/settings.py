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

    # Your apps
    'chat',
    'corsheaders',
    'rest_framework',
    'ipware',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Serve static files
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

# ================================
# DATABASE (Render PostgreSQL)
# ================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'chatsupport_db',   # DB name
        'USER': 'chatsupport_db_user',   # DB user
        'PASSWORD': 'Mbkcr08iVLof4LB86nYUanljnKRodZwd',   # Password
        'HOST': 'dpg-d2tsqgruibrs73f3qd30-a.oregon-postgres.render.com',   # Host
        'PORT': '5432',   # PostgreSQL default port
        'OPTIONS': {
            'sslmode': 'require',   # Render DB needs SSL
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
# DEFAULT PRIMARY KEY
# ================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ================================
# SERVER RUN ID (optional)
# ================================
SERVER_RUN_ID = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
