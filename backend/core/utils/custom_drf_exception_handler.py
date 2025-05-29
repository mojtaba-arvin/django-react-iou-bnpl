import traceback
from django.conf import settings
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler
from django.utils.translation import gettext_lazy as _

from core.exceptions import BusinessException
from core.utils.standard_api_response_mixin import StandardApiResponseMixin
from core.utils.error_object import ErrorObject
from core.logging.logger import get_logger
from typing import Optional, Dict, Any

logger = get_logger(__name__)


class DrfExceptionHandler:
    """
    Custom DRF exception handler that converts default error responses
    into a standardized API format.

    It transforms DRF default error formats such as:

        {
            "email": [
                "user with this email address already exists."
            ]
        }

    Into a standardized format like:

        {
            "success": false,
            "message": "Validation Error",
            "data": {},
            "errors": [
                {
                    "code": 400,
                    "message": "user with this email address already exists.",
                    "field": "email"
                }
            ]
        }

    Or transforms error responses like:

        {
            "detail": "No active account found with the given credentials"
        }

    Into:

        {
            "success": false,
            "message": "No active account found with the given credentials",
            "data": {},
            "errors": [
                {
                    "code": 401,
                    "message": "No active account found with the given credentials",
                    "field": null
                }
            ]
        }

    Reference:
        https://www.django-rest-framework.org/api-guide/exceptions/
    """
    @staticmethod
    def handle(exception: Exception, context: Optional[Dict[str, Any]]) -> Response:
        traceback.print_exc()

        if isinstance(exception, BusinessException):
            if getattr(exception, 'errors', None):
                errors = exception.errors
            else:
                errors = [ErrorObject(
                    code=exception.status_code,
                    message=str(exception.detail),
                    field=None
                ).to_dict()]
            return StandardApiResponseMixin().error_response(
                message=str(exception.detail),
                errors=errors,
                status_code=exception.status_code
            )

        # Handle DRF exceptions
        if isinstance(exception, APIException):
            # Delegate to DRF to get status_code & default data
            response = exception_handler(exception, context)

            errors = []
            data = response.data
            if isinstance(data, dict):
                # Case 1: Single error message as string under "detail"
                if 'detail' in data and isinstance(data['detail'], str):
                    errors.append(ErrorObject(
                        code=response.status_code,
                        message=data['detail'],
                        field=None
                    ).to_dict())

                # Case 2: Nested error dictionary in "detail" (e.g., JWT errors)
                elif 'detail' in data and isinstance(data['detail'], dict):
                    detail_dict = data['detail']
                    message = detail_dict.get('detail', str(detail_dict))
                    errors.append(ErrorObject(
                        code=response.status_code,
                        message=message,
                        field=None
                    ).to_dict())

                # Case 3: Field-level validation errors
                else:
                    for field, messages in data.items():
                        # Ignore symbolic error codes (e.g., "code": "token_not_valid")
                        if field == "code":
                            continue

                        if isinstance(messages, list):
                            for message in messages:
                                errors.append(ErrorObject(
                                    code=response.status_code,
                                    message=str(message),
                                    field=field
                                ).to_dict())
                        else:
                            errors.append(ErrorObject(
                                code=response.status_code,
                                message=str(messages),
                                field=field
                            ).to_dict())
            return StandardApiResponseMixin().error_response(
                message=str(_("Validation Error")),
                errors=errors,
                status_code=response.status_code
            )

        # Handle internal errors
        error_obj = ErrorObject(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=str(exception.args[0]) if exception.args else str(exception),
            details=traceback.format_exc() if settings.DEBUG else None
        )
        logger.critical(
            "unhandled_exception",
            operation="exception_handler",
            exc_info=True,
            errors=[error_obj.to_dict()]
        )
        return StandardApiResponseMixin().error_response(
            message=str(_("Unexpected server error")),
            errors=[error_obj.to_dict()],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# expose the method at the module level to use in REST_FRAMEWORK settings
drf_exception_handler = DrfExceptionHandler.handle