from django.conf import settings

# Valid credit score range
CREDIT_SCORE_MIN = 300
CREDIT_SCORE_MAX = 850

# Default credit score used in DEBUG mode for testing/demo purposes
CREDIT_SCORE_DEFAULT_DEBUG = getattr(settings, 'CREDIT_SCORE_DEBUG_DEFAULT_VALUE', CREDIT_SCORE_MIN)