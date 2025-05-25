# Import everything from base first
from .base import *

# Then override based on environment
environment = config('DJANGO_ENV', default='development')

if environment == "production":
    from .production import *
else:
    from .development import *
