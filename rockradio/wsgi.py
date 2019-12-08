"""
WSGI config for rockradio project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

if os.environ.get("ROCKRADIO_ENV") == "local":
    DJANGO_SETTINGS_MODULE = "rockradio.settings.local"
else:
    DJANGO_SETTINGS_MODULE = "rockradio.settings.production"

os.environ.setdefault("DJANGO_SETTINGS_MODULE", DJANGO_SETTINGS_MODULE)

application = get_wsgi_application()
