from typing import Iterable
from dateutil.relativedelta import relativedelta

from installment.models import Installment, InstallmentPlan


def bulk_create_installments(installment_plans: Iterable[InstallmentPlan]) -> None:
    """
    Bulk create Installment objects for the given InstallmentPlan instances.

    For each InstallmentPlan, this function:
      - Computes the base amount by dividing total_amount by installment_count.
      - Calculates due dates using the installment period and start date.
      - Adjusts the last installment to absorb any rounding discrepancies.

    Args:
        installment_plans (Iterable[InstallmentPlan]): Iterable of InstallmentPlan objects
            for which installments should be generated.

    Returns:
        None
    """
    installments: list[Installment] = []

    for installment_plan in installment_plans:
        plan = installment_plan.plan

        if not plan.installment_count:
            continue  # Skip plans without installment count

        count = plan.installment_count
        total = plan.total_amount
        base_amount = round(total / count, 2)

        for seq in range(1, count + 1):
            # Adjust final installment amount to ensure rounding consistency
            amount = (
                total - base_amount * (count - 1)
                if seq == count else base_amount
            )
            due_date = installment_plan.start_date + relativedelta(
                days=plan.installment_period * seq
            )

            installments.append(
                Installment(
                    installment_plan=installment_plan,
                    amount=amount,
                    due_date=due_date,
                    sequence_number=seq,
                )
            )

    Installment.objects.bulk_create(installments)
