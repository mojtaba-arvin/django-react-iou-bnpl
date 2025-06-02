from typing import Any

from django.db.models import Prefetch
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.contrib.auth import get_user_model

from core.pagination import DrfPagination
from core.permissions import IsMerchantForPostOnly, IsVerifiedMerchantForPostOnly, IsCustomerOrMerchant
from core.utils.response_schemas import api_error_schema, build_success_response_schema, build_error_schema
from core.utils.standard_api_response_mixin import StandardApiResponseMixin
from core.views import CheckObjectPermissionAPIView
from installment.models import InstallmentPlan, Installment
from plan.permissions import HasInstallmentPlanPermission
from plan.serializers import InstallmentPlanDetailSerializer, InstallmentPlanCreateSerializer
from plan.services.plan_queryset import InstallmentPlanQueryService

User = get_user_model()


class InstallmentPlanListCreateAPIView(StandardApiResponseMixin, generics.ListCreateAPIView):
    """API endpoint to list and create Installment Plans.

    - GET: Accessible by both merchants and customers.
    - POST: Allowed only for merchants.
    """

    permission_classes = [
        permissions.IsAuthenticated,
        IsCustomerOrMerchant,
        IsMerchantForPostOnly,
        IsVerifiedMerchantForPostOnly
    ]
    pagination_class = DrfPagination

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return InstallmentPlanCreateSerializer
        return InstallmentPlanDetailSerializer

    def get_queryset(self):
        return InstallmentPlanQueryService.get_plans_for_user(self.request.user)

    @swagger_auto_schema(
        tags=["Plans"],
        operation_description=str(_("Create a new installment plan (Merchant only)")),
        request_body=InstallmentPlanCreateSerializer,
        responses={
            status.HTTP_201_CREATED: openapi.Response(
                description=str(_("Installment plan created successfully")),
                schema=build_success_response_schema(serializer_class=InstallmentPlanCreateSerializer),
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description=str(_("Validation error")),
                schema=api_error_schema,
            ),
            status.HTTP_403_FORBIDDEN: openapi.Response(
                description=str(_("Permission denied")),
                schema=build_error_schema(
                    messages=[
                        str(_("User account is not a Merchant.")),
                        str(_("Merchant is not verified.")),
                    ]
                ),
            ),
        },
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        plan = self.perform_create(serializer)
        output = self.get_serializer(plan)

        return self.success_response(
            message=str(_("Installment plan created successfully")),
            data=output.data,
            status_code=status.HTTP_201_CREATED,
        )

    def perform_create(self, serializer: InstallmentPlanCreateSerializer) -> Any:
        return serializer.save(merchant=self.request.user)

    @swagger_auto_schema(
        tags=["Plans"],
        operation_description=str(_("List all installment plans for the current user")),
        manual_parameters=[
            openapi.Parameter(
                name='page',
                in_=openapi.IN_QUERY,
                description=str(_('Page number')),
                type=openapi.TYPE_INTEGER,
                required=False,
                default=1,
            ),
            openapi.Parameter(
                name='page_size',
                in_=openapi.IN_QUERY,
                description=str(_('Number of results per page')),
                type=openapi.TYPE_INTEGER,
                required=False,
                default=5,
            ),
        ],
        responses={
            status.HTTP_200_OK: openapi.Response(
                description=str(_("List of user installment plans")),
                schema=build_success_response_schema(
                    serializer_class=InstallmentPlanDetailSerializer,
                    many=True,
                ),
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description=str(_("Validation error")),
                schema=api_error_schema
            ),
            status.HTTP_403_FORBIDDEN: openapi.Response(
                description=str(_("Access is allowed only for customer or merchant accounts.")),
                schema=api_error_schema
            ),
        },
    )
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_success_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(
            message=str(_("List of user installment plans")),
            data=serializer.data,
        )


class InstallmentPlanDetailAPIView(
    StandardApiResponseMixin, CheckObjectPermissionAPIView, generics.GenericAPIView
):
    """
    API endpoint to retrieve the details of a specific installment plan.
    """

    serializer_class = InstallmentPlanDetailSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        HasInstallmentPlanPermission  # NOTE: needs CheckObjectPermissionAPIView
    ]
    custom_not_found_message = str(_("Installment plan not found"))  # used in CheckObjectPermissionAPIView

    # Optimized queryset to avoid N+1 queries when accessing related objects in serializer and permissions
    queryset = InstallmentPlan.objects.select_related(
        'plan',       # Fetch the related template plan in the same query
        'plan__merchant',   # Fetch the merchant to check permissions like plan.merchant == request.user
        'customer'          # Fetch customer for accessing customer.email in serializer
    ).prefetch_related(
        Prefetch(
            'installments',
            queryset=Installment.objects.order_by('due_date'),
            to_attr='ordered_installments'  # Store ordered installments in memory to avoid extra DB hits
        )
    )

    @swagger_auto_schema(
        tags=["Plans"],
        operation_description=str(_("Retrieve the detailed information of an installment plan.")),
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT),
        responses={
            status.HTTP_200_OK: openapi.Response(
                description=str(_("Successfully retrieved installment plan details.")),
                schema=build_success_response_schema(serializer_class=InstallmentPlanDetailSerializer),
            ),
            status.HTTP_403_FORBIDDEN: openapi.Response(
                description=str(_("Permission denied")),
                schema=build_error_schema(
                    messages=[
                        str(_("Merchant is not the owner of the associated template plan")),
                        str(_("Customer is not assigned to this installment plan")),
                    ]
                ),
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response(
                description=str(_("Installment plan not found")),
                schema=api_error_schema,
            ),
        },
    )
    def get(self, request: Request, pk: int, *args: Any, **kwargs: Any) -> Response:
        """Handles GET requests to retrieve the details of a specific installment plan.
    """
        installment_plan = self.get_object_with_permissions(pk=pk)
        serializer = self.get_serializer(installment_plan)
        return self.success_response(
            message=str(_("Successfully retrieved installment plan details.")),
            data=serializer.data,
        )
