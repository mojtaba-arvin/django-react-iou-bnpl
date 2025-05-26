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

# Enable Swagger UI only in development
SWAGGER_ENABLED = True
SWAGGER_API_URL = config('SWAGGER_API_URL', default='http://localhost:8000')
