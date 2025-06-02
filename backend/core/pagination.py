from django.conf import settings
from rest_framework.pagination import PageNumberPagination


class DrfPagination(PageNumberPagination):
    page_size = settings.REST_FRAMEWORK.get('PAGE_SIZE')

    # This enables the “?page_size=<n>” query parameter
    page_size_query_param = 'page_size'

    max_page_size = settings.REST_FRAMEWORK.get('MAX_PAGE_SIZE')
