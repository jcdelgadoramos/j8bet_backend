"""
Django settings for j8bet_backend project.

Generated by 'django-admin startproject' using Django 3.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

import os
import environ
from django.conf.locale.es import formats as es_formats

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
ENV = environ.Env(
    DEBUG=(bool, False),
    CORS_ORIGIN_ALLOW_ALL=(bool, False),
    ALLOWED_HOSTS=(list, []),
    CORS_ORIGIN_WHITELIST=(list, []),
)
environ.Env.read_env(os.path.join(BASE_DIR, '../.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/
ENVIRONMENTS = ENV.json('ENVIRONMENTS', default={})

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ENV('SECRET_KEY') 

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = ENV('DEBUG')

ALLOWED_HOSTS = ENV('ALLOWED_HOSTS')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

LOCAL_APPS = [
    'bets',
]

EXTERNAL_APPS = [
    'graphene_django',
]

INSTALLED_APPS = INSTALLED_APPS + LOCAL_APPS + THIRD_PARTY_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

GRAPHENE = {
    'SCHEMA': 'bets.schema.schema',
}

ROOT_URLCONF = 'j8bet_backend.urls'

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

WSGI_APPLICATION = 'j8bet_backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': ENV.db(),
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'es'

TIME_ZONE = 'America/Lima'

USE_I18N = True

USE_L10N = True

USE_TZ = True

USE_THOUSAND_SEPARATOR = True

es_formats.THOUSAND_SEPARATOR = ','
es_formats.DECIMAL_SEPARATOR = '.'

es_formats.DATETIME_FORMAT = "d/m/Y"
DATETIME_FORMAT = "%d/%m/%Y %H:%M:%S"
DATE_FORMAT = "%d/%m/%Y"
DATEMONTH_FORMAT = "%m/%Y"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'

MEDIA_URL = '/media/'

STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, '../media')

STATIC_ROOT = os.path.join(BASE_DIR, '../static')

LOGS_DIR = os.path.join(BASE_DIR, '../logs')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

DB_BACKUP_DIR = os.path.join(BASE_DIR, '../backups')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'all': {
            'format': '%(levelname)s %(asctime).16s: %(message)s',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'filters': ['require_debug_true'],
            'formatter': 'all',
        },
        'django': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filters': ['require_debug_false'],
            'filename': os.path.join(BASE_DIR, '../logs/django.log'),
            'formatter': 'all',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false']
        },
        'commands': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filters': ['require_debug_false'],
            'filename': os.path.join(BASE_DIR, '../logs/commands.log'),
            'formatter': 'all',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'django', 'mail_admins'],
            'level': 'ERROR',
        },
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console', 'django', 'mail_admins'],
        },
        'commands_log': {
            'handlers': ['console', 'mail_admins', 'commands'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': True,
        },
    },
}

LOGIN_URL = '/login/'