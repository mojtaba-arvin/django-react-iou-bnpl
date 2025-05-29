from typing import Type

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from customer.constants import CREDIT_SCORE_DEFAULT_DEBUG
from customer.models import CustomerProfile

User = get_user_model()


@receiver(post_save, sender=User)
def create_customer_profile(
    sender: Type[User], instance: User, created: bool, **kwargs: dict
) -> None:
    """Create a customer profile automatically after a new customer user is saved.

    In DEBUG mode, assigns a default credit score and marks the score as approved.

    Args:
        sender (Type[User]): The model class that sent the signal.
        instance (User): The instance of the user that was saved.
        created (bool): Indicates if the user was created.
        **kwargs (dict): Additional keyword arguments passed with the signal.

    Returns:
        None
    """

    def debug_auto_verify_credit(
        profile: CustomerProfile, score: int = CREDIT_SCORE_DEFAULT_DEBUG
    ) -> None:
        """Assign a credit score and approve in DEBUG mode only.

        Args:
            profile (CustomerProfile): The customer profile to modify.
            score (int, optional): Score to assign. Defaults to CREDIT_SCORE_DEFAULT_DEBUG.

        Returns:
            None
        """
        if not settings.DEBUG:
            return

        if profile.score_status == CustomerProfile.ScoreStatus.PENDING:
            profile.credit_score = score
            profile.score_status = CustomerProfile.ScoreStatus.APPROVED
            profile.full_clean()  # Validate score range
            profile.save()

    if created and instance.user_type == User.UserType.CUSTOMER:
        if not CustomerProfile.objects.filter(user=instance).exists():
            customer_profile = CustomerProfile.objects.create(
                user=instance,
                score_status=CustomerProfile.ScoreStatus.PENDING,
            )
            debug_auto_verify_credit(customer_profile)
            # TODO(mojtaba - 2025-05-28): Implement method to trigger external credit check via Celery task
            # or implement webhook handler to update credit_score.
