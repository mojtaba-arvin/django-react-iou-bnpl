from typing import Any

from django.utils.translation import gettext_lazy as _
from rest_framework import generics, permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from core.logging.logger import get_logger
from account.authentication.skip_invalid_jwt import SkipInvalidJWTAuthentication
from account.models import User
from core.utils.response_schemas import api_error_schema, build_success_response_schema
from core.utils.standard_api_response_mixin import StandardApiResponseMixin
from account.serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    TokenOutputSerializer,
    TokenRefreshSerializer,
    CustomTokenObtainPairSerializer,
)

logger = get_logger(__name__)


class UserRegistrationView(StandardApiResponseMixin, generics.CreateAPIView):
    """
    API endpoint to register a new user account.
    """

    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = [SkipInvalidJWTAuthentication]

    @swagger_auto_schema(
        tags=["Authentication"],
        operation_description=str(_("Register a new user")),
        request_body=UserRegistrationSerializer,
        responses={
            status.HTTP_201_CREATED: openapi.Response(
                description=str(_("User registered successfully")),
                schema=build_success_response_schema(serializer_class=UserSerializer),
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description=str(_("Validation error")),
                schema=api_error_schema,
            ),
        },
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Handle POST requests to create a new user.

        Args:
            request (Request): The incoming HTTP request.

        Returns:
            Response: A DRF Response with status 201 and serialized user data.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        output = UserSerializer(user, context={"request": request})
        headers = self.get_success_headers(output.data)

        return self.success_response(
            message=str(_("User registered successfully")),
            data=output.data,
            status_code=status.HTTP_201_CREATED,
            headers=headers,
        )

    def perform_create(self, serializer: UserRegistrationSerializer) -> User:
        """
        Save the user instance to the database.

        Args:
            serializer (UserRegistrationSerializer): The validated serializer instance.

        Returns:
            User: The created user instance.
        """
        user = serializer.save()

        logger.info(
            "user_registered",
            user_id=user.id,
            operation="user_registration"
        )
        # TODO(mojtaba - 2025-05-26): Send welcome email if needed
        return user


class CustomTokenObtainPairView(StandardApiResponseMixin, TokenObtainPairView):
    """
    API endpoint to obtain a new access and refresh JWT token pair.
    """

    serializer_class = CustomTokenObtainPairSerializer

    @swagger_auto_schema(
        tags=["Authentication"],
        operation_description=str(_("Obtain JWT token pair")),
        request_body=CustomTokenObtainPairSerializer,
        responses={
            status.HTTP_200_OK: openapi.Response(
                description=str(_("Token pair obtained")),
                schema=build_success_response_schema(serializer_class=TokenOutputSerializer),
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description=str(_("Unauthorized")),
                schema=api_error_schema,
            ),
            status.HTTP_403_FORBIDDEN: openapi.Response(
                description=str(_("User account is inactive.")),
                schema=api_error_schema,
            ),
        },
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Handle POST requests to obtain JWT token pair.

        Args:
            request (Request): The incoming HTTP request.

        Returns:
            Response: A DRF Response containing the access and refresh tokens.
        """
        response = super().post(request, *args, **kwargs)
        return self.success_response(
            message=str(_("Login successful")),
            data=response.data,
            status_code=response.status_code,
        )


class CustomTokenRefreshView(StandardApiResponseMixin, TokenRefreshView):
    """
    API endpoint to refresh the access token using a valid refresh token.
    """

    @swagger_auto_schema(
        tags=["Authentication"],
        operation_description=str(_("Refresh JWT access token")),
        request_body=TokenRefreshSerializer,
        responses={
            status.HTTP_200_OK: openapi.Response(
                description=str(_("Token refreshed successfully")),
                schema=build_success_response_schema(serializer_class=TokenOutputSerializer),
            ),
            status.HTTP_401_UNAUTHORIZED: openapi.Response(
                description=str(_("Invalid token")),
                schema=api_error_schema,
            ),
        },
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Handle POST requests to refresh JWT access token.

        Args:
            request (Request): The incoming HTTP request.

        Returns:
            Response: A DRF Response with the refreshed access token.
        """
        response = super().post(request, *args, **kwargs)
        return self.success_response(
            message=str(_("Token refreshed successfully")),
            data=response.data,
            status_code=response.status_code,
        )
