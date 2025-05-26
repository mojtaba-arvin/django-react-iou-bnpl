from rest_framework import serializers
from drf_yasg.utils import swagger_serializer_method
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

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            user_type=validated_data['user_type']
        )
        return user

    # TODO(mojtaba - 2025-05-26): Add validation logic for password strength and user_type choices.
    # Consider checking for duplicate email and handling business rules.


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
    def get_user_type_display(self, obj):
        return obj.get_user_type_display()
