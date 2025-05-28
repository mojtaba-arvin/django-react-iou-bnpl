from django.utils import timezone
from installment.models import Installment

def process_installment_payment(installment: Installment) -> Installment:
    installment.status = Installment.Status.PAID
    installment.paid_at = timezone.now()
    installment.save(update_fields=["status", "paid_at"])
    return installment
