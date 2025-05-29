from rest_framework import permissions
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework.request import Request
from rest_framework.views import View

User = get_user_model()


class IsMerchant(permissions.BasePermission):
    """
    Allows access only to authenticated users with the Merchant role.
    """
    message = _("User account is not a Merchant.")

    def has_permission(self, request: Request, view: View) -> bool:
        return (
            request.user.is_authenticated and
            getattr(request.user, "user_type", None) == User.UserType.MERCHANT
        )


class IsMerchantForPostOnly(permissions.BasePermission):
    """
    Allows POST requests only if the user is an authenticated Merchant.
    Other request methods are always allowed.
    """
    message = _("User account is not a Merchant.")

    def has_permission(self, request: Request, view: View) -> bool:
        if request.method == "POST":
            return (
                request.user.is_authenticated and
                getattr(request.user, "user_type", None) == User.UserType.MERCHANT
            )
        return True


class IsVerifiedMerchantForPostOnly(permissions.BasePermission):
    """
    Allows POST requests only if the user has a verified merchant profile.
    Other request methods are always allowed.
    """
    message = _("Merchant is not verified.")

    def has_permission(self, request: Request, view: View) -> bool:
        if request.method == "POST":
            merchant_profile = getattr(request.user, "merchant_profile", None)
            return (
                merchant_profile is not None and
                callable(getattr(merchant_profile, "can_create_payment_plan", None)) and
                merchant_profile.can_create_payment_plan()
            )
        return True
