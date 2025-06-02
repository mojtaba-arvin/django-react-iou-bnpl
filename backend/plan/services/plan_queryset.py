"""Service layer for querying installment plans with their template plan details."""

from django.contrib.auth import get_user_model
from django.db.models import Prefetch, QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import status

from core.exceptions import BusinessException
from core.logging.logger import get_logger
from installment.models import Installment, InstallmentPlan

User = get_user_model()
logger = get_logger(__name__)


class InstallmentPlanQueryService:
    """Service for retrieving installment plans with their associated template plan details."""

    @staticmethod
    def get_plans_for_user(user: User) -> QuerySet[InstallmentPlan]:
        """Retrieve installment plans with template plan details based on user type.

        Args:
            user: The authenticated user requesting the plans. Must be either a merchant
                or customer based on user_type.

        Returns:
            QuerySet[InstallmentPlan]: An optimized queryset containing:
                - For merchants: All their created installment plans with template details
                - For customers: Their assigned installment plans with template details
                - Prefetched installments ordered by due_date
                - Annotated customer counts for merchant view

        Raises:
            BusinessException: Only support for customer or merchant accounts.
        """

        if user.user_type == User.UserType.MERCHANT:
            return InstallmentPlanQueryService._get_merchant_installment_plans(user)
        elif user.user_type == User.UserType.CUSTOMER:
            return InstallmentPlanQueryService._get_customer_installment_plans(user)
        # Although user_type is usually enforced through permission classes in views,
        # this fallback handles misuse when the service is invoked directly without proper validation.
        else:
            logger.critical(
                "invalid_user_type",
                operation="get_installment_plans_for_user",
                user_id=user.id,
                user_type=user.user_type
            )
            raise BusinessException(
                message=str(_("User type not supported for this operation.")),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

    @staticmethod
    def _get_merchant_installment_plans(merchant: User) -> QuerySet[InstallmentPlan]:
        """Retrieve all installment plans created by a merchant with template details.

        Args:
            merchant: The merchant user who created the plans.

        Returns:
            QuerySet[InstallmentPlan]: Queryset with:
                - All installment plans from the merchant's template plans
                - Complete template plan details via select_related
                - Prefetched installments ordered by due_date
                - Annotated customer counts
        """
        return InstallmentPlan.objects.filter(
            plan__merchant=merchant
        ).select_related(
            'plan'  # Include all template plan details
        ).prefetch_related(
            Prefetch(
                'installments',
                queryset=Installment.objects.order_by('due_date'),
                to_attr='ordered_installments'
            ),
            'customer'  # Prefetch customer details if needed
        ).order_by(
            '-created_at'
        )

    @staticmethod
    def _get_customer_installment_plans(customer: User) -> QuerySet[InstallmentPlan]:
        """Retrieve active/completed installment plans with template details for customer.

        Args:
            customer: The customer user assigned to the plans.

        Returns:
            QuerySet[InstallmentPlan]: Queryset with:
                - Only active/completed installment plans
                - Complete template plan details via select_related
                - Merchant details via select_related
                - Prefetched installments ordered by due_date
        """
        return InstallmentPlan.objects.filter(
            customer=customer,
            status__in=[
                InstallmentPlan.Status.ACTIVE,
                InstallmentPlan.Status.COMPLETED
            ],
            # We intentionally skip filtering by plan__status=Plan.Status.ACTIVE
            # because archived plans can still have valid active/completed installment plans
            # plan__status=Plan.Status.ACTIVE,
        ).select_related(
            'plan',  # Include all template plan details
            'plan__merchant'  # Include merchant details
        ).prefetch_related(
            Prefetch(
                'installments',
                queryset=Installment.objects.order_by('due_date'),
                to_attr='ordered_installments'
            )
        ).order_by(
            '-created_at'
        )