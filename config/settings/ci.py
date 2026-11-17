"""CI settings using the same PostgreSQL engine as production."""

import os

from .base import *  # noqa: F401, F403

DEBUG = False
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "erp_test"),
        "USER": os.getenv("DB_USER", "erp_test"),
        "PASSWORD": os.getenv("DB_PASSWORD", "erp_test"),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "5432"),
        "CONN_MAX_AGE": 0,
        "TEST": {"NAME": "test_erp_test"},
    }
}

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
CACHES = {
    "default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}
}
REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"] = [
    "rest_framework.permissions.AllowAny",
]
REST_FRAMEWORK["DEFAULT_PAGINATION_CLASS"] = None
REST_FRAMEWORK["PAGE_SIZE"] = None
