import os
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent
ENV = environ.Env(
    DEBUG=(bool, False),
    CORS_ORIGIN_ALLOW_ALL=(bool, False),
    ALLOWED_HOSTS=(list, []),
    CORS_ORIGIN_WHITELIST=(list, []),
)
environ.Env.read_env(os.path.join(BASE_DIR, "../.env"))

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

LOCAL_APPS = [
    "bets",
]

THIRD_PARTY_APPS = [
    "graphene_django",
]

INSTALLED_APPS = INSTALLED_APPS + LOCAL_APPS + THIRD_PARTY_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

GRAPHENE = {
    "SCHEMA": "j8bet_backend.graphql.api.schema",
}

ROOT_URLCONF = "j8bet_backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'test_cache',
    }
}

PASSWORD_HASHERS = ("django.contrib.auth.hashers.MD5PasswordHasher",)

SYSTEM_ENV = os.environ.get('SYSTEM_ENV', None)

SECRET_KEY = "TESTING_KEY"

DEBUG = True

if SYSTEM_ENV == "GITHUB_WORKFLOW":
    DATABASES = {
        "default": {
           "ENGINE": "django.db.backends.postgresql",
           "NAME": "test_db",
           "USER": "test_user",
           "PASSWORD": "test_pwd",
           "HOST": "db",
           "PORT": "5432",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "test_db",
            "TEST": {"NAME": "test_db",},
            "USER": ENV.db().get("USER"),
            "PASSWORD": ENV.db().get("PASSWORD"),
            "HOST": ENV.db().get("HOST"),
        }
    }
