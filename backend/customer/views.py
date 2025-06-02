from typing import Any
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from core.pagination import DrfPagination
from core.permissions import IsMerchant
from customer.selectors import get_eligible_customers_for_merchant
from customer.serializers import EligibleCustomerSerializer
from core.utils.standard_api_response_mixin import StandardApiResponseMixin
from core.utils.response_schemas import api_error_schema, build_success_response_schema


class EligibleCustomerListAPIView(StandardApiResponseMixin, generics.ListAPIView):
    """
    API endpoint to list eligible customers for the merchant.
    """

    serializer_class = EligibleCustomerSerializer
    permission_classes = [permissions.IsAuthenticated, IsMerchant]
    pagination_class = DrfPagination

    def get_queryset(self):
        return get_eligible_customers_for_merchant()

    @swagger_auto_schema(
        tags=["Customers"],
        operation_description=str(_("List eligible customers (Merchant only)")),
        responses={
            status.HTTP_200_OK: openapi.Response(
                description=str(_("List of eligible customers")),
                schema=build_success_response_schema(
                    serializer_class=EligibleCustomerSerializer,
                    many=True
                )
            ),
            status.HTTP_403_FORBIDDEN: openapi.Response(
                description=str(_("Permission denied")),
                schema=api_error_schema
            )
        },
    )
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_success_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(
            message=str(_("List of eligible customers")),
            data=serializer.data
        )
