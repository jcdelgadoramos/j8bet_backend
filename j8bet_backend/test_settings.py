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

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'test_cache',
    }
}

PASSWORD_HASHERS = ("django.contrib.auth.hashers.MD5PasswordHasher",)

if SYSTEM_ENV == "GITHUB_WORKFLOW":
    DEBUG = True
    SECRET_KEY = "TESTING_KEY"
    DATABASES = {
        "default": {
           "ENGINE": "django.db.backends.postgresql",
           "NAME": "test_db",
           "USER": "test_user",
           "PASSWORD": "test_pwd",
           "HOST": "127.0.0.1",
           "PORT": "5432",
        }
    }
