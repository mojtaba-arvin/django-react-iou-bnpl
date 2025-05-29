from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils.translation import gettext_lazy as _

from core.logging.logger import get_logger

logger = get_logger(__name__)


class ActiveUserJWTAuthentication(JWTAuthentication):
    """
    Reject tokens if the user is inactive (even if token is valid).
    """

    def get_user(self, validated_token):
        user = super().get_user(validated_token)

        if not user.is_active:
            logger.error(
                "user_inactive",
                user_id=user.id,
                operation="user_authentication"
            )
            raise AuthenticationFailed(_("User account is inactive."), code="user_inactive")

        return user
