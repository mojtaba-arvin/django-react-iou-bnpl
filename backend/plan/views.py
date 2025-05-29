from typing import Any
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.contrib.auth import get_user_model
from core.permissions import IsMerchantForPostOnly, IsVerifiedMerchantForPostOnly
from plan.serializers import PlanSerializer
from plan.selectors import get_plans_for_user
from core.utils.response_schemas import api_error_schema, build_success_response_schema, build_error_schema
from core.utils.standard_api_response_mixin import StandardApiResponseMixin

User = get_user_model()


class PlanListCreateAPIView(StandardApiResponseMixin, generics.ListCreateAPIView):
    """
    API endpoint to list and create payment plans for a merchant.
    """

    serializer_class = PlanSerializer
    permission_classes = [permissions.IsAuthenticated, IsMerchantForPostOnly, IsVerifiedMerchantForPostOnly]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return get_plans_for_user(self.request.user)

    @swagger_auto_schema(
        tags=["Plans"],
        operation_description=str(_("Create a new payment plan (Merchant only)")),
        request_body=PlanSerializer,
        responses={
            status.HTTP_201_CREATED: openapi.Response(
                description=str(_("Plan created successfully")),
                schema=build_success_response_schema(serializer_class=PlanSerializer),
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
            message=str(_("Plan created successfully")),
            data=output.data,
            status_code=status.HTTP_201_CREATED,
        )

    def perform_create(self, serializer: PlanSerializer) -> Any:
        return serializer.save(merchant=self.request.user)

    @swagger_auto_schema(
        tags=["Plans"],
        operation_description=str(_("List all plans for the current user")),
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
                description=str(_("List of user plans")),
                schema=build_success_response_schema(
                    serializer_class=PlanSerializer,
                    many=True,
                ),
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description=str(_("Validation error")),
                schema=api_error_schema
            )
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
            message=str(_("List of user plans")),
            data=serializer.data,
        )
