from typing import Optional, Tuple

from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed

from core.logging.logger import get_logger

logger = get_logger(__name__)


class SkipInvalidJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication class that skips invalid or expired tokens
    and allows the request to continue as an anonymous user.

    This is useful for public endpoints (e.g. registration or public info)
    where authentication is optional. If a token is valid, the user is authenticated.
    If the token is invalid or expired, authentication is skipped silently.

    Warning:
        Use this only on endpoints where authentication is truly optional.
        If used improperly, it may expose protected resources to unauthenticated access.
    """

    def authenticate(self, request: Request) -> Optional[Tuple[object, str]]:
        """
        Try to authenticate the request using JWT. Skip silently on invalid or expired tokens.

        Args:
            request (Request): The incoming HTTP request.

        Returns:
            Optional[Tuple[object, str]]: The user and token if authentication is successful,
            otherwise None to allow anonymous access.
        """
        try:
            return super().authenticate(request)
        except (AuthenticationFailed, InvalidToken) as exc:
            logger.warning(
                "JWT authentication skipped due to invalid or expired token",
                extra={
                    "path": request.path,
                    "operation": "jwt_authenticate",
                    "error": str(exc),
                }
            )
            return None
