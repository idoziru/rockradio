# pylint: skip-file
import os
from decouple import config
from .base import *

WSGI_APPLICATION = "rockradio.wsgi.application"

DEBUG = False

ALLOWED_HOSTS = [
    "rockradio.dimafilatov.ru",
    "185.87.199.139",
    "127.0.0.1",
    "www.rockradio.dimafilatov.ru",
]

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "rockradio",
        "USER": "rockradio",
        "PASSWORD": "LP274dcgWpFQLP274d",
        "HOST": "localhost",
        "PORT": "",
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {"format": "{levelname} {message}", "style": "{",},
    },
    "filters": {
        "require_debug_true": {"()": "django.utils.log.RequireDebugTrue",},
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
        },
        "file": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": os.path.join(BASE_DIR, "logs", "django.log"),
        },
    },
    "loggers": {
        "django": {"handlers": ["console"], "propagate": True,},
        "django.request": {
            "handlers": ["mail_admins", "file"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}
