# pylint: skip-file
# type: ignore

from .base import *

# Use export ROCKRADIO_ENV=local to automaticaly use local settings
DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1"]

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}
