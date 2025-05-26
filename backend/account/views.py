from django.utils.translation import gettext_lazy as _
from rest_framework import generics, permissions, status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from core.utils.response_schemas import api_error_schema, build_success_response_schema
from core.utils.standard_api_response_mixin import StandardApiResponseMixin
from account.serializers import UserRegistrationSerializer, UserSerializer


class UserRegistrationView(StandardApiResponseMixin, generics.CreateAPIView):
    """
    Register a new user account.
    """

    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        tags=['Authentication'],
        operation_description="Register a new user",
        request_body=UserRegistrationSerializer,
        responses={
            status.HTTP_201_CREATED: openapi.Response(
                description=str(_("User registered successfully")),
                schema=build_success_response_schema(serializer_class=UserSerializer)
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description=str(_("Validation error")),
                schema=api_error_schema,
            )
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        output = UserSerializer(user, context={'request': request})
        headers = self.get_success_headers(output.data)

        return self.success_response(
            message=str(_("User registered successfully")),
            data=output.data,
            status_code=status.HTTP_201_CREATED,
            headers=headers
        )

    def perform_create(self, serializer):
        user = serializer.save()
        # TODO (mojtaba - 2025-05-26): Send welcome email if needed
        # TODO (mojtaba - 2025-05-26): Implement info logging level about user created.
        return user
