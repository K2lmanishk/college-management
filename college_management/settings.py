from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv
from django.contrib.messages import constants as message_constants

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-change-me')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = [h.strip() for h in os.environ.get('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',') if h.strip()]

RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

CSRF_TRUSTED_ORIGINS = [o.strip() for o in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',') if o.strip()]
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f'https://{RENDER_EXTERNAL_HOSTNAME}')

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'accounts',
    'academics',
    'finance',
    'communication',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'college_management.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
            'college_management.context_processors.college_info',
        ],
    },
}]

WSGI_APPLICATION = 'college_management.wsgi.application'

DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",  # local fallback when DATABASE_URL is not set
        conn_max_age=600,
    )
}
# To use PostgreSQL, install psycopg2-binary and uncomment:
# DATABASES['default'] = {
#     'ENGINE': 'django.db.backends.postgresql',
#     'NAME': os.environ.get('DB_NAME'),
#     'USER': os.environ.get('DB_USER'),
#     'PASSWORD': os.environ.get('DB_PASSWORD'),
#     'HOST': os.environ.get('DB_HOST', 'localhost'),
#     'PORT': os.environ.get('DB_PORT', '5432'),
# }

AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {
        'BACKEND': (
            'django.contrib.staticfiles.storage.StaticFilesStorage' if DEBUG
            else 'whitenoise.storage.CompressedManifestStaticFilesStorage'
        ),
    },
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'

# Map Django message levels to Bootstrap alert classes
MESSAGE_TAGS = {message_constants.ERROR: 'danger'}

# College info
COLLEGE_NAME = "College Management System"
COLLEGE_ADDRESS = "Greater Noida, UP 201301"
COLLEGE_CONTACT = "+91-7004514869"
COLLEGE_EMAIL = "info@risecollege.edu.in"
ACADEMIC_YEAR = "2025-2026"

# Twilio (set in .env)
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER', '')
