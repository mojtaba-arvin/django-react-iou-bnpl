from decimal import Decimal
from django.db.models import Sum
from typing import Dict

from installment.models import Installment
from plan.models import Plan
from account.models import User


class MerchantDashboardService:
    """Service class to calculate various dashboard metrics for a merchant."""

    def __init__(self, merchant: User) -> None:
        """
        Initialize the MerchantDashboardService with a merchant.

        Args:
            merchant (User): The merchant for whom the dashboard metrics are calculated.
        """
        self.merchant = merchant
        self.installments = self._get_installments()

    def _get_installments(self) -> Installment:
        """Retrieve installments associated with the merchant's plans.

        Returns:
            QuerySet: A QuerySet of Installments associated with the merchant.
        """
        return Installment.objects.filter(
            installment_plan__plan__merchant=self.merchant
        )

    def get_total_revenue(self) -> Decimal:
        """Calculate and return the total revenue from paid installments.

        Returns:
            Decimal: Total revenue from installments with 'PAID' status, or 0.00 if none.
        """
        return self.installments.filter(status=Installment.Status.PAID).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')

    def get_success_rate(self) -> float:
        """Calculate the success rate of installments (paid vs total).

        Returns:
            float: Success rate as a percentage, or 0.0 if no installments.
        """
        total = self.installments.count()
        paid = self.installments.filter(status=Installment.Status.PAID).count()
        return (paid / total * 100) if total else 0.0

    def get_overdue_count(self) -> int:
        """Get the count of overdue installments.

        Returns:
            int: Number of installments with 'LATE' status.
        """
        return self.installments.filter(status=Installment.Status.LATE).count()

    def get_active_plans(self) -> int:
        """Get the count of active plans for the merchant.

        Returns:
            int: Number of active plans associated with the merchant.
        """
        return Plan.objects.filter(
            merchant=self.merchant,
            status=Plan.Status.ACTIVE
        ).count()

    def get_metrics(self) -> Dict[str, float]:
        """Retrieve all the key metrics for the merchant dashboard.

        Returns:
            Dict[str, float]: A dictionary containing total revenue, success rate,
            overdue count, and active plans.
        """
        return {
            'total_revenue': self.get_total_revenue(),
            'success_rate': self.get_success_rate(),
            'overdue_count': self.get_overdue_count(),
            'active_plans': self.get_active_plans(),
        }
