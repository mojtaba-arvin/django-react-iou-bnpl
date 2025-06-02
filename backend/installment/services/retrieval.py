"""Service layer for installment retrieval operations."""
from datetime import date
from typing import Optional

from django.contrib.auth import get_user_model
from django.db.models import QuerySet, Q

from installment.constants import InstallmentStatusFilters
from installment.models import Installment

User = get_user_model()


class InstallmentRetrievalService:
    """Service for retrieving customer installments with progress information."""

    def __init__(self, customer: User) -> None:
        """Initialize with customer user.

        Args:
            customer: The customer user instance.
        """
        self.customer = customer

    def get_customer_installments(
        self, status_filter: Optional[str] = None
    ) -> QuerySet:
        """Get installments for customer with optional status filtering.

        Business Rules:
        - UPCOMING: Installments that are either:
          * Not yet due (due_date >= today) AND unpaid (status = PENDING)
          * Or due today but still unpaid
        - PAST: Installments that are either:
          * Already paid (regardless of due date)
          * Or past due (due_date < today) even if unpaid

        Args:
            status_filter: Optional status filter ('upcoming' or 'past').

        Returns:
            QuerySet: Filtered queryset of installments.
        """
        queryset = Installment.objects.filter(
            installment_plan__customer=self.customer
        ).select_related("installment_plan", "installment_plan__plan").order_by("due_date")

        today = date.today()

        if status_filter == InstallmentStatusFilters.UPCOMING:
            queryset = queryset.filter(
                Q(status=Installment.Status.PENDING) &
                Q(due_date__gte=today)
            )
        elif status_filter == InstallmentStatusFilters.PAST:
            queryset = queryset.filter(
                Q(status=Installment.Status.PAID) |
                Q(due_date__lt=today)
            )

        return queryset
