"""Views for installment related operations."""
from typing import Any, List

from django.db.models import QuerySet, Prefetch
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, permissions, status
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from core.exceptions import BusinessException
from core.pagination import DrfPagination
from core.permissions import IsCustomer
from core.views import CheckObjectPermissionAPIView
from core.utils.response_schemas import (
    api_error_schema,
    build_success_response_schema,
    build_error_schema,
)
from core.utils.standard_api_response_mixin import StandardApiResponseMixin
from core.logging.logger import get_logger
from installment.constants import InstallmentStatusFilters
from installment.models import Installment, InstallmentPlan
from installment.permissions import IsInstallmentCustomer
from installment.serializers import (
    CustomerFacingInstallmentSerializer,
    InstallmentFilterSerializer,
)
from installment.services.payment import process_installment_payment
from installment.services.retrieval import InstallmentRetrievalService

logger = get_logger(__name__)


class InstallmentPaymentAPIView(
    StandardApiResponseMixin, CheckObjectPermissionAPIView, generics.GenericAPIView
):
    """API endpoint to pay a specific installment.

    Only the owner customer is allowed to pay their installments.
    """

    serializer_class = CustomerFacingInstallmentSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsInstallmentCustomer,  # NOTE: needs CheckObjectPermissionAPIView
    ]
    custom_not_found_message = str(_("Installment not found"))  # used in CheckObjectPermissionAPIView

    # Optimized queryset to avoid N+1 queries in permissions and serializer:
    queryset = Installment.objects.select_related(
        'installment_plan',                 # Access to installment.installment_plan
        'installment_plan__customer',       # Access to installment.installment_plan.customer
        'installment_plan__plan',           # Access to installment.installment_plan.plan
    ).prefetch_related(
        Prefetch(
            'installment_plan__installments',  # Prefetch all installments for checking previous unpaid ones
            queryset=Installment.objects.only(
                'id',
                'sequence_number',
                'status',
                'installment_plan_id',
                'installment_plan__customer_id',
            ),  # Minimize columns fetched
            to_attr='prefetched_installments',  # Store in a temporary in-memory attribute
        )
    )

    @swagger_auto_schema(
        tags=["Installments"],
        operation_description=str(_("Pay a specific installment (Customer only)")),
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT),
        responses={
            status.HTTP_200_OK: openapi.Response(
                description=str(_("Installment paid successfully")),
                schema=build_success_response_schema(serializer_class=CustomerFacingInstallmentSerializer),
            ),
            status.HTTP_403_FORBIDDEN: openapi.Response(
                description=str(_("Permission denied")),
                schema=api_error_schema,
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response(
                description=str(_("Installment not found")),
                schema=api_error_schema,
            ),
            status.HTTP_409_CONFLICT: openapi.Response(
                description=str(_("Installment conflict")),
                schema=build_error_schema(
                    messages=[
                        str(_("Installment already paid.")),
                        str(_("Cannot pay installment because the plan is not active.")),
                        str(_("Previous installments must be paid before this one.")),
                    ]
                ),
            ),
        },
    )
    def post(self, request: Request, pk: int, *args: Any, **kwargs: Any) -> Response:
        """Process payment for a specific installment.

        Args:
            request: The HTTP request object.
            pk: Primary key of the installment to pay.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response: HTTP response indicating success or failure.

        Raises:
            NotFound: If installment doesn't exist.
            BusinessException: For various payment conflicts.
        """
        try:
            installment = self.get_object_with_permissions(pk=pk)
        except Installment.DoesNotExist:
            logger.error(
                "not_found",
                user_id=self.request.user.id,
                installment_id=pk,
                operation="installment_payment",
            )
            raise NotFound(detail=_("Installment not found"))

        if installment.status == Installment.Status.PAID:
            logger.error(
                "already_paid",
                user_id=self.request.user.id,
                installment_paid_at=installment.paid_at,
                operation="installment_payment",
            )
            raise BusinessException(
                message=str(_("Installment already paid.")),
                status_code=status.HTTP_409_CONFLICT,
            )

        if installment.installment_plan.status != InstallmentPlan.Status.ACTIVE:
            logger.error(
                "not_active_installment_plan",
                user_id=self.request.user.id,
                installment_plan_status=installment.installment_plan.status,
                operation="installment_payment",
            )
            raise BusinessException(
                message=str(_("Cannot pay because the installment plan is not active.")),
                status_code=status.HTTP_409_CONFLICT,
            )

        previous_unpaid_qs = installment.installment_plan.installments.filter(
            installment_plan__customer=installment.installment_plan.customer,
            sequence_number__lt=installment.sequence_number,
            status__in=[
                Installment.Status.PENDING,
                Installment.Status.LATE,
                Installment.Status.FAILED,
            ],
        )

        if previous_unpaid_qs.exists():
            logger.error(
                "previous_unpaid",
                user_id=self.request.user.id,
                attempted_sequence_number=installment.sequence_number,
                unpaid_installments=list(
                    previous_unpaid_qs.values_list("id", "sequence_number", "status")
                ),
                operation="installment_payment",
            )
            raise BusinessException(
                message=str(_("Previous installments must be paid before this one.")),
                status_code=status.HTTP_409_CONFLICT,
            )

        installment = process_installment_payment(installment)
        serializer = self.get_serializer(installment)
        return self.success_response(
            message=str(_("Installment paid successfully")),
            data=serializer.data,
        )


class InstallmentListAPIView(StandardApiResponseMixin, generics.ListAPIView):
    """API endpoint to list installments with filtering.

    Supports:
    - Filtering by status (upcoming/past)
    - Pagination
    """

    serializer_class = CustomerFacingInstallmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomer]
    pagination_class = DrfPagination
    filter_serializer_class = InstallmentFilterSerializer

    def get_queryset(self) -> QuerySet[Installment]:
        """Get filtered queryset of installments for the current customer.

        Returns:
            List[Installment]: Filtered list of installments.
        """
        filter_serializer = self.filter_serializer_class(data=self.request.query_params)
        filter_serializer.is_valid(raise_exception=True)

        service = InstallmentRetrievalService(self.request.user)
        status_filter = self.request.query_params.get("status")
        return service.get_customer_installments(status_filter=status_filter)

    @swagger_auto_schema(
        tags=["Installments"],
        operation_description=str(_("List all installments for the current customer")),
        manual_parameters=[
            openapi.Parameter(
                name="status",
                in_=openapi.IN_QUERY,
                description=InstallmentStatusFilters.get_help_text(),
                type=openapi.TYPE_STRING,
                enum=[choice[0] for choice in InstallmentStatusFilters.CHOICES],
                required=False,
            ),
        ],
        responses={
            status.HTTP_200_OK: openapi.Response(
                description=str(_("List of customer installments")),
                schema=build_success_response_schema(
                    serializer_class=CustomerFacingInstallmentSerializer,
                    many=True,
                ),
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description=str(_("Invalid status filter")),
                schema=api_error_schema,
            ),
            status.HTTP_403_FORBIDDEN: openapi.Response(
                description=str(_("User account is not a Customer.")),
                schema=api_error_schema,
            ),
        },
    )
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """List installments with optional filtering and pagination.

        Args:
            request: The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response: Paginated list of installments.
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_success_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(
            message=str(_("Installment list retrieved successfully")),
            data=serializer.data,
        )