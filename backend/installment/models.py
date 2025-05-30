from datetime import date

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import AbstractTimestampedModel
from plan.models import Plan

User = get_user_model()


class InstallmentPlan(AbstractTimestampedModel):
    """Represents a customer's installment plan derived from a payment plan."""

    class Status(models.TextChoices):
        """Enumeration of possible installment plan statuses."""
        ACTIVE = 'active', _('Active')
        COMPLETED = 'completed', _('Completed')
        DEFAULTED = 'defaulted', _('Defaulted')

    plan: models.ForeignKey = models.ForeignKey(
        Plan,
        on_delete=models.PROTECT,
        related_name='installment_plans',
        help_text=_('The payment plan template used to generate installments.'),
    )
    customer: models.ForeignKey = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='installment_plans',
        limit_choices_to={'user_type': User.UserType.CUSTOMER},
        help_text=_('The customer associated with this installment plan.'),
    )
    start_date: models.DateField = models.DateField(
        _('start date'),
        default=date.today,
        help_text=_('Date when the first installment is due.'),
    )
    status: models.CharField = models.CharField(
        _('status'),
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
        help_text=_('Current lifecycle status of the installment plan.'),
    )

    def __str__(self) -> str:
        """Return a readable identifier for the installment plan."""
        return f"Installment Plan #{self.id}"

    class Meta:
        verbose_name = _('installment plan')
        verbose_name_plural = _('installment plans')
        ordering = ['-created_at']


class Installment(AbstractTimestampedModel):
    """Represents an individual installment payment within an InstallmentPlan."""

    class Status(models.TextChoices):
        """Enumeration of possible installment statuses."""
        PENDING = 'pending', _('Pending')
        PAID = 'paid', _('Paid')
        LATE = 'late', _('Late')
        FAILED = 'failed', _('Failed')

    installment_plan: models.ForeignKey = models.ForeignKey(
        InstallmentPlan,
        on_delete=models.CASCADE,
        related_name='installments',
        help_text=_('The associated installment plan.'),
    )
    amount = models.DecimalField(
        _('amount'),
        max_digits=12,
        decimal_places=2,
        help_text=_('Amount due for this installment.'),
    )
    due_date = models.DateField(
        _('due date'),
        help_text=_('Date when this installment is due.'),
    )
    status = models.CharField(
        _('status'),
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        help_text=_('Current payment status of the installment.'),
    )
    sequence_number = models.PositiveSmallIntegerField(
        _('installment number'),
        help_text=_('Sequential position of this installment in the plan.'),
    )
    paid_at = models.DateTimeField(
        _('paid at'),
        null=True,
        blank=True,
        help_text=_('Timestamp when the installment was paid.'),
    )

    def __str__(self) -> str:
        """Return a readable identifier for the installment."""
        return f"Installment #{self.sequence_number}"

    class Meta:
        verbose_name = _('installment')
        verbose_name_plural = _('installments')
        ordering = ['sequence_number']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gt=0),
                name='installment_amount_positive',
            ),
            models.UniqueConstraint(
                fields=['installment_plan', 'sequence_number'],
                name='unique_installment_sequence_per_plan',
            ),
            models.UniqueConstraint(
                fields=['installment_plan', 'due_date'],
                name='unique_due_date_per_plan',
            ),
        ]
