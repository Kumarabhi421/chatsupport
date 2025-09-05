from pathlib import Path
import os
import random
import string

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ================================
# SECURITY
# ================================
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-dev-key")

# Production me DEBUG False rakho
DEBUG = os.getenv("DEBUG", "True") == "True"

# Render har deploy pe alag domain deta hai, safest option:
ALLOWED_HOSTS = ["*"]

# Render CSRF trusted origin
CSRF_TRUSTED_ORIGINS = [
    "https://chatsupport-1.onrender.com",
    "https://chatsupport-ruq6.onrender.com",
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
    'chat',
    'corsheaders',
    'rest_framework',
    'ipware',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
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
# DATABASE
# ================================
# Local MySQL (for development) – Render ke liye DATABASE_URL use karna better hai
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv("DB_NAME", "mychatdb"),
        'USER': os.getenv("DB_USER", "root"),
        'PASSWORD': os.getenv("DB_PASSWORD", "1234"),
        'HOST': os.getenv("DB_HOST", "localhost"),
        'PORT': os.getenv("DB_PORT", "3306"),
        'OPTIONS': {
            'charset': 'utf8mb4',
        }
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
# STATIC FILES
# ================================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"

# ================================
# DEFAULT PRIMARY KEY
# ================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ================================
# SERVER RUN ID (NEW PART)
# ================================
SERVER_RUN_ID = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
