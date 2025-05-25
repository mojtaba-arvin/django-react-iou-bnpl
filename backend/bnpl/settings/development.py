from .base import *
from decouple import config, Csv


DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*', cast=Csv())

INSTALLED_APPS = INSTALLED_APPS + [
    'django_extensions',
]

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True