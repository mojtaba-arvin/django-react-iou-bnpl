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

# Default credit score assigned to new customer profiles in DEBUG mode only.
# This value is used *only* during development and testing for simulated credit checks.
# Do NOT import this setting directly in your app code.
# Instead, always import `CREDIT_SCORE_DEFAULT_DEBUG` from `customers/constants.py`.
CREDIT_SCORE_DEBUG_DEFAULT_VALUE = config('CREDIT_SCORE_DEBUG_DEFAULT_VALUE', default=600, cast=int)
