from decimal import Decimal
from django.db.models import Sum, Count, Q
from typing import Dict

from installment.models import Installment, InstallmentPlan
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
        # Base queryset of installments for the merchant
        self.installments = Installment.objects.filter(
            installment_plan__plan__merchant=self.merchant
        )

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

    def get_active_installment_plans(self) -> int:
        """Get the count of active installment plans for the merchant.

        Returns:
            int: Number of active plans associated with the merchant.
        """
        return InstallmentPlan.objects.filter(
            plan__merchant=self.merchant,
            status=Plan.Status.ACTIVE
        ).count()

    def get_metrics(self) -> Dict[str, Decimal]:
        """Retrieve all the key metrics for the merchant dashboard.

        Returns:
            Dict[str, float]: A dictionary containing total revenue, success rate,
            overdue count, and active plans.
        """
        # Aggregate multiple metrics in one database hit
        agg = self.installments.aggregate(
            total_revenue=Sum('amount', filter=Q(status=Installment.Status.PAID)),
            total_count=Count('id'),
            paid_count=Count('id', filter=Q(status=Installment.Status.PAID)),
            overdue_count=Count('id', filter=Q(status=Installment.Status.LATE)),
            active_plans=Count(
                'installment_plan',
                filter=Q(
                    installment_plan__plan__merchant=self.merchant,
                    installment_plan__status=InstallmentPlan.Status.ACTIVE
                ),
                distinct=True
            )
        )

        total = agg.get('total_count') or 0
        paid = agg.get('paid_count') or 0

        success_rate = (paid / total * 100) if total else 0.0

        # Format numerical values to two decimal places for display
        formatted_metrics = {
            'total_revenue': f"{(agg.get('total_revenue') or Decimal('0.00')):.2f}",
            'success_rate': f"{success_rate:.2f}",
            'overdue_count': str(agg.get('overdue_count') or 0),
            'active_plans': str(agg.get('active_plans') or 0),
        }

        return formatted_metrics
