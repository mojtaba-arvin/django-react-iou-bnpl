from rest_framework import generics, permissions, status
from django.utils.translation import gettext_lazy as _
from rest_framework.request import Request
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from analytics.serializers import MerchantDashboardMetricsSerializer
from analytics.services.merchant_dashboard_service import MerchantDashboardService
from core.exceptions import BusinessException
from core.permissions import IsMerchant
from core.utils.standard_api_response_mixin import StandardApiResponseMixin
from core.utils.response_schemas import (
    api_error_schema,
    build_success_response_schema
)
from core.logging.logger import get_logger

logger = get_logger(__name__)


class MerchantDashboardAPIView(StandardApiResponseMixin, generics.GenericAPIView):
    """Retrieve dashboard metrics for authenticated merchant."""

    serializer_class = MerchantDashboardMetricsSerializer
    permission_classes = [permissions.IsAuthenticated, IsMerchant]

    @swagger_auto_schema(
        tags=["Analytics"],
        operation_description=str(_("Get metrics for merchant dashboard")),
        responses={
            status.HTTP_200_OK: openapi.Response(
                description=str(_("Merchant dashboard metrics retrieved successfully")),
                schema=build_success_response_schema(
                    serializer_class=MerchantDashboardMetricsSerializer
                ),
            ),
            status.HTTP_403_FORBIDDEN: openapi.Response(
                description=str(_("Permission denied")),
                schema=api_error_schema
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response(
                description=str(_("Dashboard data generation failed")),
                schema=api_error_schema
            ),
        },
    )
    def get(self, request: Request, *args, **kwargs) -> Response:
        """Handle GET request to retrieve merchant dashboard metrics.

        Args:
            request (Request): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: A Response object containing the dashboard metrics or error message.
        """

        service = MerchantDashboardService(request.user)
        data = service.get_metrics()
        serializer = self.get_serializer(data=data)

        if not serializer.is_valid():
            logger.critical(
                "invalid_dashboard_serializer",
                operation="dashboard_metrics_serialization",
                errors=serializer.errors,
                user_id=request.user.id
            )
            raise BusinessException(
                message=str(_("Dashboard data generation failed")),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return self.success_response(
            message=str(_("Merchant dashboard metrics retrieved successfully")),
            data=serializer.data
        )
