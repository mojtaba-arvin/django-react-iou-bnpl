from typing import Any, Dict
from rest_framework import serializers
from drf_yasg.utils import swagger_serializer_method
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'user_type')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data: Dict[str, Any]) -> User:
        """
        Create and return a new user with the given validated data.

        Args:
            validated_data (dict): Dictionary of validated fields.

        Returns:
            User: The created user instance.
        """
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            user_type=validated_data['user_type']
        )
        return user

        # TODO(mojtaba - 2025-05-26): Add password strength and user_type validation.
        # Consider handling duplicate email gracefully.


class UserSerializer(serializers.ModelSerializer):
    """
    General-purpose serializer for User objects.
    Can be used for retrieve, list, update, and as output for registration.
    """
    user_type_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'user_type',
            'user_type_display',
            'is_active',
        )
        read_only_fields = fields

    @swagger_serializer_method(serializer_or_field=serializers.CharField)
    def get_user_type_display(self, obj: User) -> str:
        return obj.get_user_type_display()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
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
        token['user_type'] = user.user_type
        token['email'] = user.email
        return token


class TokenRefreshSerializer(serializers.Serializer):
    refresh: str = serializers.CharField()


class TokenOutputSerializer(serializers.Serializer):
    access: str = serializers.CharField()
    refresh: str = serializers.CharField()
