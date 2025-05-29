from celery import shared_task
from installment.services.status import mark_overdue_installments

@shared_task
def check_overdue_installments() -> None:
    """Check and mark overdue installments.

    This task will invoke the `mark_overdue_installments` function to
    update the status of installments that are overdue.

    Returns:
        None
    """
    mark_overdue_installments()
