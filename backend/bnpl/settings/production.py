from .base import *

# Production security
DEBUG = False
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

# Additional production security settings
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True

# CORS settings
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [] # TODO