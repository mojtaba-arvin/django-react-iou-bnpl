from datetime import date
from installment.models import Installment

def mark_overdue_installments() -> None:
    """Mark installments with past due dates as overdue.

    This function checks for all installments that are still marked as PENDING
    and have a due date earlier than today's date, then updates their status
    to LATE.

    Returns:
        None
    """
    overdue_installments = Installment.objects.filter(
        due_date__lt=date.today(),
        status=Installment.Status.PENDING
    )

    # Update the status of overdue installments
    overdue_installments.update(status=Installment.Status.LATE)
