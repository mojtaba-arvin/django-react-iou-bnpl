"""Service layer for installment retrieval operations."""
from datetime import date
from typing import Optional

from django.contrib.auth import get_user_model
from django.db.models import QuerySet, Q, Case, When, Value, BooleanField, Exists, OuterRef
from django.utils.translation import gettext_lazy as _
from rest_framework import status

from core.logging.logger import get_logger
from core.exceptions import BusinessException
from installment.constants import InstallmentStatusFilters
from installment.models import Installment, InstallmentPlan

User = get_user_model()
logger = get_logger(__name__)


class InstallmentRetrievalService:
    """Service for retrieving customer installments with progress information."""

    def __init__(self, customer: User, raise_validation_errors: bool = False) -> None:
        """Initialize with customer user.

        Args:
            customer: The customer user instance
            raise_validation_errors: If True, raises BusinessException for invalid payments
        """
        self.customer = customer
        self.raise_validation_errors = raise_validation_errors

    def get_customer_installments(
        self,
        status_filter: Optional[str] = None,
    ) -> QuerySet:
        """Get installments for customer with optional status filtering.

        Business Rules:
        - UPCOMING: Installments that are either:
          * Not yet due (due_date >= today) AND unpaid (status = PENDING)
          * Or due today but still unpaid
        - PAST: Installments that are either:
          * Already paid (regardless of due date)
          * Or past due (due_date < today) even if unpaid

        Additionally, we add a field `is_payable`, which is True only if:
          * The installment is not paid.
          * The installment plan is active.
          * There are no previous unpaid installments (with lower sequence_number) in the same plan.

        Args:
            status_filter: Optional status filter ('upcoming' or 'past').

        Returns:
            QuerySet: Filtered queryset of installments with annotated `is_payable`.
        """
        # Subquery to check for any previous unpaid installments in the same plan
        previous_unpaid = Installment.objects.filter(
            installment_plan=OuterRef('installment_plan'),
            sequence_number__lt=OuterRef('sequence_number'),
            status__in=[
                Installment.Status.PENDING,
                Installment.Status.LATE,
                Installment.Status.FAILED,
            ]
        )

        # Base queryset with annotations
        queryset = Installment.objects.filter(
            installment_plan__customer=self.customer
        ).select_related(
            "installment_plan", "installment_plan__plan"
        ).annotate(
            is_payable=Case(
                # Condition 1: Already paid -> not payable
                When(status=Installment.Status.PAID, then=Value(False)),
                # Condition 2: Installment plan not active -> not payable
                When(~Q(installment_plan__status=InstallmentPlan.Status.ACTIVE), then=Value(False)),
                # Condition 3: Has previous unpaid installments -> not payable
                When(Exists(previous_unpaid), then=Value(False)),
                # Default case: payable
                default=Value(True),
                output_field=BooleanField()
            )
        )

        today = date.today()

        # Apply status filtering
        if status_filter == InstallmentStatusFilters.UPCOMING:
            queryset = queryset.filter(
                Q(status=Installment.Status.PENDING) & Q(due_date__gte=today)
            )
            # Order to see the installments that are due soon.
            return queryset.order_by("due_date", "sequence_number")
        elif status_filter == InstallmentStatusFilters.PAST:
            queryset = queryset.filter(
                Q(status=Installment.Status.PAID) | Q(due_date__lt=today)
            )
            # Order to see the last paid installments
            return queryset.order_by("-paid_at")

        # Order by recent plan, upcoming seq
        return queryset.order_by("-installment_plan__id", "sequence_number")

    def validate_installment_payment(self, installment: Installment) -> bool:
        """Validate if the installment can be paid according to business rules.

        Returns:
            bool: True if payable, False if not

        Raises:
            BusinessException: If raise_validation_errors=True and the installment isn't payable
        """

        if installment.status == Installment.Status.PAID:
            if not self.raise_validation_errors:
                return False
            logger.error(
                "already_paid",
                user_id=self.customer.id,
                installment_paid_at=installment.paid_at,
                operation="installment_payment",
            )
            raise BusinessException(
                message=str(_("Installment already paid.")),
                status_code=status.HTTP_409_CONFLICT,
            )

        if installment.installment_plan.status != InstallmentPlan.Status.ACTIVE:
            if not self.raise_validation_errors:
                return False
            logger.error(
                "not_active_installment_plan",
                user_id=self.customer.id,
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
            if not self.raise_validation_errors:
                return False
            logger.error(
                "previous_unpaid",
                user_id=self.customer.id,
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

        return True
