from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from merchant.models import MerchantProfile

User = get_user_model()


@receiver(post_save, sender=User)
def create_merchant_profile(sender: type[User], instance: User, created: bool, **kwargs) -> None:
    """Automatically create and optionally auto-verify merchant profile when a new merchant user is created.

    This signal is triggered after saving a User instance.

    Args:
        sender (type[User]): The User model class that triggered the signal.
        instance (User): The actual User instance that was saved.
        created (bool): True if a new user was created, False if updated.
        **kwargs: Additional keyword arguments (ignored here).

    Returns:
        None
    """

    def debug_auto_verify_merchant(profile: MerchantProfile) -> None:
        """Auto-verify merchants in DEBUG mode for local development or testing purposes.

        Args:
            profile (MerchantProfile): The merchant profile instance to verify.

        Returns:
            None
        """
        if not settings.DEBUG:
            return

        profile.is_verified = True
        profile.save()

    if not created or instance.user_type != User.UserType.MERCHANT:
        return

    if not MerchantProfile.objects.filter(user=instance).exists():
        merchant_profile = MerchantProfile.objects.create(user=instance)
        debug_auto_verify_merchant(merchant_profile)
        # TODO(mojtaba - 2025-05-28): In production, implement manual approval
        # or a periodic verification task via KYC or external API.
