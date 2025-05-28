from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from account.models import User
from core.models import AbstractTimestampedModel
from customer.constants import CREDIT_SCORE_MIN, CREDIT_SCORE_MAX


class CustomerProfileQuerySet(models.QuerySet):

    def eligible(self) -> models.QuerySet:
        """
        Filter customer profiles that are active and approved.

        Returns:
            models.QuerySet: Filtered queryset of eligible customer profiles.
        """
        return self.filter(
            is_active=True,
            score_status=self.model.ScoreStatus.APPROVED,
        ).select_related('user').only('user__email')


class CustomerProfileManager(models.Manager):

    def get_queryset(self) -> CustomerProfileQuerySet:
        return CustomerProfileQuerySet(self.model, using=self._db)

    def eligible(self) -> models.QuerySet:
        return self.get_queryset().eligible()


class CustomerProfile(AbstractTimestampedModel):
    """Customer profile model for BNPL service.

    Stores credit score information and score validation status
    for users registered as customers.
    """

    class ScoreStatus(models.TextChoices):
        """Validation status of the credit score."""
        PENDING = 'pending', _('Pending Validation')
        APPROVED = 'approved', _('Validated')
        REJECTED = 'rejected', _('Rejected')

    objects = CustomerProfileManager()

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='customer_profile',
        verbose_name=_('user'),
        help_text=_('Reference to the Customer user account'),
        db_index=True
    )
    credit_score = models.IntegerField(
        _('credit score'),
        null=True,
        blank=True,
        validators=[
            MinValueValidator(CREDIT_SCORE_MIN, _('Minimum credit score is %(limit_value)s')),
            MaxValueValidator(CREDIT_SCORE_MAX, _('Maximum credit score is %(limit_value)s')),
        ],
        help_text=_('External credit score; populate after credit check'),
    )
    score_status = models.CharField(
        _('score status'),
        max_length=20,
        choices=ScoreStatus.choices,
        default=ScoreStatus.PENDING,
        db_index=True,
        help_text=_('Current status of credit score validation'),
    )

    is_active = models.BooleanField(
        _('active status'),
        default=True,
        db_index=True,
        help_text=_('Can this customer use BNPL services?'),
    )

    def __str__(self) -> str:
        """Return the user's email as the string representation."""
        return self.user.email

    class Meta:
        verbose_name = _('customer profile')
        verbose_name_plural = _('customer profiles')
        ordering = ['-created_at']
        # TODO(mojtaba - 2025-05-28): Uncomment to add a constraint for approved status requiring a non-null credit score
        # constraints = [
        #     models.CheckConstraint(
        #         check=(
        #                 models.Q(score_status='approved', credit_score__isnull=False) |
        #                 ~models.Q(score_status='approved')
        #         ),
        #         name='approved_requires_credit_score_not_null'
        #     )
        # ]
