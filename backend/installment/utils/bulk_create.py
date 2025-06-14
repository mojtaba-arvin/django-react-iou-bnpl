from decimal import Decimal
from typing import Iterable
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import status

from core.exceptions import BusinessException
from core.logging.logger import get_logger
from installment.models import Installment, InstallmentPlan

logger = get_logger(__name__)


def bulk_create_installments(installment_plans: Iterable[InstallmentPlan]) -> None:
    """
    Bulk create Installment objects for the given InstallmentPlan instances.

    For each InstallmentPlan, this function:
      - Computes the base amount by dividing total_amount by installment_count.
      - Calculates due dates using the installment period and start date.
      - Adjusts the last installment to absorb any rounding discrepancies.
      - Validates amounts are positive before creation.

    Args:
        installment_plans (Iterable[InstallmentPlan]): Iterable of InstallmentPlan objects
            for which installments should be generated.

    Returns:
        None

    Raises:
        ValueError: If any calculated installment amount would be invalid
    """
    installments: list[Installment] = []

    for installment_plan in installment_plans:
        plan = installment_plan.plan
        # Skip invalid plans (should be prevented by validation)
        if not plan.installment_count or plan.installment_count <= 0:
            logger.critical(
                "invalid_plan_installment_count",
                operation="bulk_create_installments",
                user_id=plan.merchant.id,
                installment_count=plan.installment_count
            )
            continue
        if plan.total_amount <= 0:
            logger.critical(
                "invalid_plan_total_amount",
                operation="bulk_create_installments",
                user_id=plan.merchant.id,
                total_amount=plan.total_amount
            )
            continue

        count = plan.installment_count
        total = Decimal(str(plan.total_amount))  # Ensure Decimal

        # Convert total to cents using rounding to nearest cent
        total_cents = int((total * 100).to_integral_value())
        base_cents = total_cents // count
        remainder = total_cents % count  # Extra cents to distribute

        for seq in range(1, count + 1):
            # Distribute extra cents to first 'remainder' installments
            cents = base_cents + (1 if seq <= remainder else 0)
            amount = Decimal(cents) / Decimal(100)

            # Validate amount is positive
            if amount <= 0:
                logger.critical(
                    "invalid_calc_installment_amount",
                    operation="bulk_create_installments",
                    user_id=plan.merchant.id,
                    plan_id=plan.id,
                    installment_plan_id=installment_plan.id,
                    sequence_number=seq,
                    base_cents=base_cents,
                    calc_amount=amount
                )
                raise BusinessException(
                    message=str(_("An issue occurred while creating installments.")),
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
                )

            # Calculate due date (n-1 periods after start)
            due_date = installment_plan.start_date + relativedelta(
                days=plan.installment_period * (seq - 1)
            )

            installments.append(
                Installment(
                    installment_plan=installment_plan,
                    amount=amount,
                    due_date=due_date,
                    sequence_number=seq,
                )
            )

    # Validate all installments before bulk create
    for installment in installments:
        try:
            installment.full_clean()
        except ValidationError:
            logger.critical(
                "validation_error_on_installment_full_clean",
                operation="bulk_create_installments",
                exc_info=True,
                user_id=installment.installment_plan.plan.merchant.id,
                plan_id=installment.installment_plan.plan.id,
                plan_total_amount=installment.installment_plan.plan.total_amount,
                installment_plan_id=installment.installment_plan.id,
                installment_amount=installment.amount,
                sequence_number=installment.sequence_number,
            )
            raise BusinessException(
                message=str(_("An issue occurred while creating installments.")),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

    Installment.objects.bulk_create(installments)
