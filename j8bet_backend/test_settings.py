import environ

from pathlib import Path

from .settings import *


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
        "TEST": {
            "NAME": "test_db",
        },
        "USER": ENV.db().get("USER"),
        "PASSWORD": ENV.db().get("PASSWORD"),
        "HOST": ENV.db().get("HOST")
    }
}

PASSWORD_HASHERS = (
    "django.contrib.auth.hashers.MD5PasswordHasher",
)
