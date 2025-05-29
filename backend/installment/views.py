from typing import Any

from django.utils.translation import gettext_lazy as _
from rest_framework import generics, permissions, status
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from core.exceptions import BusinessException
from core.views import CheckObjectPermissionAPIView
from core.utils.response_schemas import api_error_schema, build_success_response_schema, build_error_schema
from core.utils.standard_api_response_mixin import StandardApiResponseMixin
from core.logging.logger import get_logger

from installment.models import Installment, InstallmentPlan
from installment.permissions import IsInstallmentCustomer
from installment.serializers import InstallmentSerializer
from installment.services.payment import process_installment_payment

logger = get_logger(__name__)


class InstallmentPaymentAPIView(StandardApiResponseMixin, CheckObjectPermissionAPIView, generics.GenericAPIView):
    """
    API endpoint to pay a specific installment. Only the owner customer is allowed.
    """

    serializer_class = InstallmentSerializer
    queryset = Installment.objects.select_related("installment_plan__customer")
    permission_classes = [
        permissions.IsAuthenticated,
        IsInstallmentCustomer  # NOTE: needs CheckObjectPermissionAPIView to check has_object_permission
    ]

    @swagger_auto_schema(
        tags=["Installments"],
        operation_description=str(_("Pay a specific installment (Customer only)")),
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT),
        responses={
            status.HTTP_200_OK: openapi.Response(
                description=str(_("Installment paid successfully")),
                schema=build_success_response_schema(serializer_class=InstallmentSerializer),
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
        }
    )
    def post(self, request: Request, pk: int, *args: Any, **kwargs: Any) -> Response:
        try:
            installment = self.get_object_with_permissions(pk=pk)
        except Installment.DoesNotExist:
            logger.error(
                "not_found",
                user_id=self.request.user.id,
                installment_id=pk,
                operation="installment_payment"
            )
            raise NotFound(detail=_("Installment not found"))

        if installment.status == Installment.Status.PAID:
            logger.error(
                "already_paid",
                user_id=self.request.user.id,
                installment_paid_at=installment.paid_at,
                operation="installment_payment"
            )
            raise BusinessException(
                message=str(_("Installment already paid.")),
                status_code=status.HTTP_409_CONFLICT
            )

        if installment.installment_plan.status != InstallmentPlan.Status.ACTIVE:
            logger.error(
                "not_active_installment_plan",
                user_id=self.request.user.id,
                installment_plan_status=installment.installment_plan.status,
                operation="installment_payment"
            )
            raise BusinessException(
                message=str(_("Cannot pay because the installment plan is not active.")),
                status_code=status.HTTP_409_CONFLICT
            )

        previous_unpaid_qs = installment.installment_plan.installments.filter(
            installment_plan__customer=installment.installment_plan.customer,
            sequence_number__lt=installment.sequence_number,
            status__in=[Installment.Status.PENDING, Installment.Status.LATE, Installment.Status.FAILED],
        )

        if previous_unpaid_qs.exists():
            logger.error(
                "previous_unpaid",
                user_id=self.request.user.id,
                attempted_sequence_number=installment.sequence_number,
                unpaid_installments=list(
                    previous_unpaid_qs.values_list("id", "sequence_number", "status")
                ),
                operation="installment_payment"
            )
            raise BusinessException(
                message=str(_("Previous installments must be paid before this one.")),
                status_code=status.HTTP_409_CONFLICT
            )

        installment = process_installment_payment(installment)

        serializer = self.get_serializer(installment)
        return self.success_response(
            message=str(_("Installment paid successfully")),
            data=serializer.data,
        )
