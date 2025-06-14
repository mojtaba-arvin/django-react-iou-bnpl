from datetime import date
from typing import List, overload, Optional, Union
from django.db import transaction
from django.contrib.auth import get_user_model

from core.logging.logger import get_logger
from plan.constants import DEFAULT_INSTALLMENT_PERIOD
from installment.models import InstallmentPlan
from installment.signals import skip_installment_creation, enable_installment_creation
from installment.utils.bulk_create import bulk_create_installments
from plan.models import Plan

User = get_user_model()
logger = get_logger(__name__)


class PlanCreatorService:
    """Service for creating a plan (template) and installment plan(s).

    Depending on whether you pass a single customer or a list,
    it will either:
      - Create one InstallmentPlan and return it (new API version), or
      - Create multiple InstallmentPlans in bulk and return the Plan (old API version).
    """

    @overload
    def __init__(
        self,
        *,
        merchant: User,
        name: str,
        total_amount: float,
        installment_count: int,
        installment_period: int,
        customer: User,
        start_date: date = ...,
        plan_status: str = ...
    ) -> None:
        """single-customer-version: returns InstallmentPlan."""

    @overload
    def __init__(
        self,
        *,
        merchant: User,
        name: str,
        total_amount: float,
        installment_count: int,
        installment_period: int,
        customers: List[User],
        start_date: date = ...,
        plan_status: str = ...
    ) -> None:
        """bulk-version: returns Plan."""

    def __init__(self, *, merchant: User, name: str, total_amount: float,
                 installment_count: int, installment_period: int = DEFAULT_INSTALLMENT_PERIOD,
                 customers: List[User], start_date: date = date.today(),
                 plan_status: str = Plan.Status.ACTIVE):
        """Initialize the service with merchant, plan details, and customers.

        Args:
            merchant (User): The merchant creating the plan.
            name (str): The name of the plan.
            total_amount (float): The total amount of the plan.
            installment_count (int): The number of installments.
            installment_period (int): The period between installments in days (default is 30 days).
            customers (List[User]): The list of customers associated with the plan.
            start_date (date): Start date for the installment plan (defaults to today).
            plan_status (str): The status of the plan (default is active).
        """
        self.merchant = merchant
        self.name = name
        self.total_amount = total_amount
        self.installment_count = installment_count
        self.installment_period = installment_period
        self.customers = customers
        self.start_date = start_date
        self.plan_status = plan_status

    def __init__(
        self,
        *,
        merchant: User,
        name: str,
        total_amount: float,
        installment_count: int,
        installment_period: int,
        customer: Optional[User] = None,
        customers: Optional[List[User]] = None,
        start_date: date = date.today(),
        plan_status: str = Plan.Status.ACTIVE
    ) -> None:
        """
        Args:
            merchant: Merchant creating the plan.
            name: Plan name.
            total_amount: Total amount.
            installment_count: Number of installments.
            installment_period: Days between installments.
            customer: Single customer.
            customers: Multiple customers (bulk-version).
            start_date: When installments begin.
            plan_status: Initial plan status.
        """
        if bool(customer) == bool(customers):
            logger.critical(
                "customer_and_customers_conflict",
                operation="plan_creation_service_init",
                user_id=merchant.id
            )
            raise ValueError("Provide exactly one of `customer` or `customers`.")

        self.merchant = merchant
        self.name = name
        self.total_amount = total_amount
        self.installment_count = installment_count
        self.installment_period = installment_period
        self.customer = customer
        self.customers = customers
        self.start_date = start_date
        self.plan_status = plan_status

    def execute(self) -> Union[InstallmentPlan, Plan]:
        """Create the Plan and associated installment plan(s).

        Returns:
            - InstallmentPlan if `customer` was provided.
            - Plan if `customers` was provided.
        """
        with transaction.atomic():
            # Create the plan
            plan = Plan.objects.create(
                merchant=self.merchant,
                name=self.name,
                total_amount=self.total_amount,
                installment_count=self.installment_count,
                installment_period=self.installment_period,
                status=self.plan_status,
            )

            # Single-customer flow
            # All related Installments will be created automatically by Signal.
            if self.customer:
                # -------------------------------------------------------------------
                # We need `ordered_installments` immediately available on the returned
                # InstallmentPlan so our DetailSerializer (source='ordered_installments')
                # can render them without issuing another DB query.
                #
                # But Django’s bulk_create() bypasses post_save signals entirely, and
                # our normal post-save handler (which would create installments in
                # response to plan.save()) would either not run or run at the wrong time.
                #
                # Therefore, we:
                #   1. Temporarily disable the post-save signal handler
                #   2. Create the InstallmentPlan (skipping the handler)
                #   3. Manually generate installments via bulk_create_installments()
                #   4. Read them into memory (ordered by due_date) and attach
                #      as `ordered_installments`
                #   5. Re-enable the signal for future operations
                # This guarantees `inst_plan.ordered_installments` is populated and
                # correctly ordered before we return.
                # -------------------------------------------------------------------

                # Disable signal temporarily to prevent auto-installment creation
                skip_installment_creation()
                installment_plan = InstallmentPlan.objects.create(
                    plan=plan,
                    customer=self.customer,
                    start_date=self.start_date,
                )
                # Re-enable signal to allow future installment creation
                enable_installment_creation()

                # Create installments for the plans
                bulk_create_installments([installment_plan])

                ordered = list(installment_plan.installments.order_by('due_date'))
                setattr(installment_plan, 'ordered_installments', ordered)

                return installment_plan

            # Multi-customer flow
            installment_plans = [
                InstallmentPlan(
                    plan=plan,
                    customer=customer,
                    start_date=self.start_date
                )
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
