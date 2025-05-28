import threading
from typing import Type

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import InstallmentPlan, Installment
from .utils.bulk_create import bulk_create_installments

# Thread-local flag to control signal execution
_skip_signal = threading.local()


def skip_installment_creation() -> None:
    """Set a thread-local flag to skip signal-based installment creation."""
    _skip_signal.value = True


def enable_installment_creation() -> None:
    """Unset the flag so signal-based installment creation can proceed."""
    _skip_signal.value = False


def is_signal_skipped() -> bool:
    """Check whether installment creation should be skipped.

    Returns:
        bool: True if installment creation is skipped, False otherwise.
    """
    return getattr(_skip_signal, 'value', False)


@receiver(post_save, sender=InstallmentPlan)
def create_installments(
    sender: Type[InstallmentPlan],
    instance: InstallmentPlan,
    created: bool,
    **kwargs,
) -> None:
    """Automatically generate installments when a new InstallmentPlan is created.

    Args:
        sender (Type[InstallmentPlan]): The model class.
        instance (InstallmentPlan): The newly created InstallmentPlan instance.
        created (bool): True if a new object was created.
        **kwargs: Additional keyword arguments.
    """
    if not created or is_signal_skipped():
        return

    bulk_create_installments(installment_plans=[instance])


@receiver(post_save, sender=Installment)
def update_installment_plan_status(
    sender: Type[Installment],
    instance: Installment,
    **kwargs,
) -> None:
    """Update the status of InstallmentPlan to COMPLETED when all installments are paid.

    Args:
        sender (Type[Installment]): The model class.
        instance (Installment): The updated Installment instance.
        **kwargs: Additional keyword arguments.
    """
    if instance.status != Installment.Status.PAID:
        return

    plan = instance.installment_plan

    # If any installment is not paid, do not update status
    if plan.installments.exclude(status=Installment.Status.PAID).exists():
        return

    if plan.status != InstallmentPlan.Status.COMPLETED:
        plan.status = InstallmentPlan.Status.COMPLETED
        plan.save(update_fields=["status"])
