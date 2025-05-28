from typing import Any, Dict

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from drf_yasg.utils import swagger_serializer_method

from account.services.user_service import UserService

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    Validates email uniqueness, password strength, and delegates
    user creation to the UserService.
    """

    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message=_("A user with this email already exists."),
            )
        ],
        help_text=_("Unique email address for the user."),
    )
    password = serializers.CharField(
        write_only=True,
        help_text=_("User password (write-only)."),
    )

    class Meta:
        model = User
        fields = ("email", "password", "user_type")
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate_password(self, value: str) -> str:  # noqa: R0201 pylint:disable=no-self-use
        """
        Validate password strength using Django's validators.

        Args:
            value: The password string to validate.

        Returns:
            The original password if valid.

        Raises:
            serializers.ValidationError: If password validations fail.
        """
        try:
            validate_password(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(detail=exc.messages)
        return value

    def create(self, validated_data: Dict[str, Any]) -> User:
        """
        Create a new User via UserService.

        Args:
            validated_data (dict): Dictionary of validated fields including email, password, and user_type.

        Returns:
            User: The created user instance.
        """
        return UserService.register_user(
            email=validated_data["email"],
            password=validated_data["password"],
            user_type=validated_data["user_type"],
        )


class UserSerializer(serializers.ModelSerializer):
    """
    General-purpose serializer for User objects.

    Includes a display field for user_type.
    """

    user_type_display = serializers.SerializerMethodField(
        help_text=_("Human-readable user type."),
    )

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "user_type",
            "user_type_display",
            "is_active",
        )
        read_only_fields = fields

    @swagger_serializer_method(serializer_or_field=serializers.CharField)
    def get_user_type_display(self, obj: User) -> str:
        """
        Return the display value of the user's type.

        Args:
            obj: The User instance.

        Returns:
            A human-readable string for user_type.
        """
        return obj.get_user_type_display()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    JWT serializer that adds custom claims to the token.
    """

    @classmethod
    def get_token(cls, user: User) -> Any:
        """
        Add custom claims to the JWT token.

        Args:
            user (User): Authenticated user.

        Returns:
            Token: Token object with additional claims.
        """
        token = super().get_token(user)
        token["user_type"] = user.user_type
        token["email"] = user.email
        return token


class TokenRefreshSerializer(serializers.Serializer):  # noqa: WPS230
    """
    Serializer for refreshing JWT tokens.
    """

    refresh = serializers.CharField(
        help_text=_("The refresh token."),
    )


class TokenOutputSerializer(serializers.Serializer):  # noqa: WPS230
    """
    Output serializer for JWT token pair responses.
    """

    access = serializers.CharField(
        help_text=_("The access token."),
    )
    refresh = serializers.CharField(
        help_text=_("The refresh token."),
    )
