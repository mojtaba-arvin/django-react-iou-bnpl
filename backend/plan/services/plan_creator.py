from typing import List
from django.db import transaction

from plan.constants import DEFAULT_INSTALLMENT_PERIOD
from installment.models import InstallmentPlan
from installment.signals import skip_installment_creation, enable_installment_creation
from installment.utils.bulk_create import bulk_create_installments
from plan.models import Plan
from django.contrib.auth import get_user_model

User = get_user_model()


class PlanCreatorService:
    """Service for creating a new plan with associated installment plans for customers."""

    def __init__(self, *, merchant: User, name: str, total_amount: float,
                 installment_count: int, installment_period: int = DEFAULT_INSTALLMENT_PERIOD,
                 customers: List[User]):
        """Initialize the service with merchant, plan details, and customers.

        Args:
            merchant (User): The merchant creating the plan.
            name (str): The name of the plan.
            total_amount (float): The total amount of the plan.
            installment_count (int): The number of installments.
            installment_period (int): The period between installments in days (default is 30 days).
            customers (List[User]): The list of customers associated with the plan.
        """
        self.merchant = merchant
        self.name = name
        self.total_amount = total_amount
        self.installment_count = installment_count
        self.installment_period = installment_period
        self.customers = customers

    def execute(self) -> Plan:
        """Create the plan and associated installment plans for the customers.

        This method creates a new plan, assigns it to the customers, and creates the related
        installment plans. The plan status is set to ACTIVE. Installment creation is handled
        in bulk, and signals are temporarily disabled to avoid unwanted behavior.

        Returns:
            Plan: The newly created plan.
        """
        with transaction.atomic():
            # Create the plan
            plan = Plan.objects.create(
                merchant=self.merchant,
                name=self.name,
                total_amount=self.total_amount,
                installment_count=self.installment_count,
                installment_period=self.installment_period,
                status=Plan.Status.ACTIVE,
            )

            # Create InstallmentPlans for each customer
            installment_plans = [
                InstallmentPlan(plan=plan, customer=customer)
                for customer in self.customers
            ]

            # Disable signal temporarily to prevent auto-installment creation
            skip_installment_creation()
            InstallmentPlan.objects.bulk_create(installment_plans)

            # Re-enable signal to allow future installment creation
            enable_installment_creation()

            # Create installments for the plans
            bulk_create_installments(installment_plans)

        return plan
