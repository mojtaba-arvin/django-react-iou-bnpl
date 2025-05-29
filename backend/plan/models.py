from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from core.models import AbstractTimestampedModel
from plan.constants import DEFAULT_INSTALLMENT_PERIOD

User = get_user_model()


class Plan(AbstractTimestampedModel):
    """Represents a payment plan template created by a merchant."""

    class Status(models.TextChoices):
        """Enumeration of possible Plan statuses."""
        DRAFT = 'draft', _('Draft')
        ACTIVE = 'active', _('Active')
        ARCHIVED = 'archived', _('Archived')

    merchant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='plans',
        limit_choices_to={'user_type': User.UserType.MERCHANT},
        help_text=_('The merchant user who owns this plan.'),
        db_index=True,
    )
    name = models.CharField(
        _('plan name'),
        max_length=128,
        help_text=_('Descriptive name for this payment plan.'),
    )
    total_amount = models.DecimalField(
        _('total amount'),
        max_digits=12,
        decimal_places=2,
        help_text=_('Total sum to be paid across all installments.'),
    )
    installment_count = models.PositiveSmallIntegerField(
        _('number of installments'),
        help_text=_('Total number of equal installments.'),
    )
    installment_period = models.PositiveSmallIntegerField(
        _('installment period (days)'),
        default=DEFAULT_INSTALLMENT_PERIOD,
        help_text=_('Interval in days between installments.'),
    )
    status = models.CharField(
        _('status'),
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        help_text=_('Current lifecycle status of the plan.'),
    )

    def __str__(self) -> str:
        """Return the human-readable name of the plan."""
        return self.name

    def clean(self) -> None:
        """Ensure that total amount and installment count are consistent."""
        if self.installment_count <= 0:
            raise ValidationError(_('Installment count must be greater than zero.'))
        if self.total_amount <= 0:
            raise ValidationError(_('Total amount must be greater than zero.'))

    class Meta:
        verbose_name = _('plan')
        verbose_name_plural = _('plans')
        ordering = ['-created_at']
