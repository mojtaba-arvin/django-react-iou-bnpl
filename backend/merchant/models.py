from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from account.models import User
from core.models import AbstractTimestampedModel


class MerchantProfile(AbstractTimestampedModel):
    """Merchant profile model for BNPL service.

    Stores essential merchant information required for creating payment plans.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='merchant_profile',
        verbose_name=_('user'),
        help_text=_('Reference to the Merchant user account'),
        db_index=True,
    )
    business_name = models.CharField(
        _('business name'),
        max_length=255,
        blank=True,
        default='',
        help_text=_('Official business name for payment plans; optional until later completion')
    )
    business_registration_number = models.CharField(
        _('registration number'),
        max_length=20,
        null=True,
        blank=True,
        help_text=_('Required for financial compliance; must be unique when provided')
    )
    is_verified = models.BooleanField(
        _('verified status'),
        default=False,
        db_index=True,
        help_text=_(
            'Must be True to allow merchant to create payment plans. '
            'Verified status can be set manually by an admin or automatically via a periodic task (e.g., KYC check).'
        )
    )

    def can_create_payment_plan(self) -> bool:
        """Check if merchant is allowed to create payment plans.

        Returns:
            bool: True if merchant is verified, otherwise False.
        """
        return self.is_verified

    def __str__(self) -> str:
        return self.business_name

    class Meta:
        verbose_name = _('merchant profile')
        verbose_name_plural = _('merchant profiles')
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['business_registration_number'],
                condition=~Q(business_registration_number__isnull=True),
                name='unique_business_reg_number_if_not_null'
            )
        ]
