"""
Django settings for uniwaybackend project.
"""

from pathlib import Path
import os

import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'info.log'),
            'when': 'midnight',
            'interval': 1,
            'backupCount': 90,
            'formatter': 'verbose',
        },
    },
    'formatters': {
        'verbose': {
            'format': '{asctime}: {message} ({levelname})',
            'style': '{',
        },
    },
    'loggers': {
        'uniway-backend': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

SECRET_KEY = 'django-insecure-_kw!!o=2_!4e-bvwq(21&=wnh#x!oa%@d68ci=!+oe$e5kdxwq'

DEBUG = True

# ✅ FIXED: added local IP
ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    '10.0.2.2',
    '192.168.1.43',      # 👈 REQUIRED for physical phone
    '159.65.144.35',
    'uniwaymaitreyi.in',
    'www.uniwaymaitreyi.in',
]

CSRF_TRUSTED_ORIGINS = [
    'https://uniwaymaitreyi.in',
    'https://www.uniwaymaitreyi.in',
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://10.0.2.2:8000',
    'http://192.168.1.43:8000',   # 👈 ADD THIS
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'rest_framework.authtoken',
    'main',
    'widget_tweaks',
    'captcha',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'main.authentication.UserLessTokenAuthentication'
    ]
}

AUTH_TOKEN_MODEL = 'main.models.CustomToken'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'uniwaybackend.urls'

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

WSGI_APPLICATION = 'uniwaybackend.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'uniway',
        'USER': 'uniway_user',
        'PASSWORD': 'uniway789',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'static_root')

MEDIA_URL = '/images/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'static/images')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ✅ FIXED CORS (simple + safe for dev)
CORS_ALLOW_ALL_ORIGINS = True

import uniwaybackend.firebase
