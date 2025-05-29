from celery import shared_task
from datetime import date, timedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string
from installment.models import Installment


@shared_task
def send_payment_reminders() -> None:
    """
    Send email reminders for installments due in 3 days.

    This task queries all pending installments with a due date
    exactly 3 days from today and sends a reminder email to the
    corresponding customer.
    """
    reminder_date: date = date.today() + timedelta(days=3)
    upcoming = Installment.objects.filter(
        due_date=reminder_date,
        status=Installment.Status.PENDING
    ).select_related('installment_plan__customer')

    for installment in upcoming:
        send_installment_reminder(installment)


def send_installment_reminder(installment: Installment) -> None:
    """
    Send a reminder email for a specific installment.

    Args:
        installment (Installment): The installment for which to send a reminder.
    """
    subject: str = f"Upcoming payment reminder: Due on {installment.due_date}"
    message: str = render_to_string('payment_reminder.txt', {
        'customer': installment.installment_plan.customer,
        'amount': installment.amount,
        'due_date': installment.due_date,
        'plan': installment.installment_plan.plan.name,
    })

    send_mail(
        subject=subject,
        message=message,
        from_email='notifications@bnpl.com',
        recipient_list=[installment.installment_plan.customer.email],
        fail_silently=False
    )
