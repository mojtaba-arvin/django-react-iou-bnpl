from typing import Optional, Dict, Any, List
from rest_framework.response import Response
from rest_framework import status
from django.utils.translation import gettext_lazy as _


class StandardApiResponseMixin:
    """
    A standardized API response mixin for consistent success and error responses.
    Compatible with DRF and Swagger.
    """

    @staticmethod
    def _build_response(
        success: bool,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        errors: Optional[List[Dict[str, Any]]] = None,
        status_code: int = status.HTTP_200_OK,
        pagination: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Response:
        """
        Build a standardized API response.

        Args:
            success: Boolean indicating if the request was successful
            message: Human-readable message describing the result
            data: Main payload of the response (for successful requests)
            errors: List of error details (for failed requests)
            status_code: HTTP status code
            pagination: Pagination metadata (for paginated responses)
            headers: Optional dict of HTTP headers to include in the response

        Returns:
            DRF Response object with standardized format and headers
        """
        response_data: Dict[str, Any] = {
            "success": success,
            "message": message,
            "data": data if data is not None else {},
            "errors": errors if errors is not None else [],
        }

        if pagination is not None:
            response_data["pagination"] = pagination

        return Response(response_data, status=status_code, headers=headers)

    def success_response(
        self,
        message: str = str(_("Operation completed successfully")),
        data: Optional[Dict[str, Any]] = None,
        status_code: int = status.HTTP_200_OK,
        pagination: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Response:
        """
        Standard success response.
        """
        return self._build_response(
            success=True,
            message=message,
            data=data,
            status_code=status_code,
            pagination=pagination,
            headers=headers,
        )


    def error_response(
        self,
        message: str = str(_("An error occurred")),
        errors: Optional[List[Dict[str, Any]]] = None,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        headers: Optional[Dict[str, str]] = None,
    ) -> Response:
        """
        Standard error response.
        """
        if errors is None:
            errors = [{"code": status_code, "message": message}]

        return self._build_response(
            success=False,
            message=message,
            errors=errors,
            status_code=status_code,
            headers=headers,
        )

    # Common HTTP status responses
    def created_response(
        self,
        message: str = _("Resource created successfully"),
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Response:
        return self.success_response(message, data, status_code=status.HTTP_201_CREATED, headers=headers)

    def not_found_response(
        self,
        message: str = _("Resource not found"),
        headers: Optional[Dict[str, str]] = None,
    ) -> Response:
        return self.error_response(message, status_code=status.HTTP_404_NOT_FOUND, headers=headers)

    def forbidden_response(
        self,
        message: str = _("Permission denied"),
        headers: Optional[Dict[str, str]] = None,
    ) -> Response:
        return self.error_response(message, status_code=status.HTTP_403_FORBIDDEN, headers=headers)

    def unauthorized_response(
        self,
        message: str = _("Authentication required"),
        headers: Optional[Dict[str, str]] = None,
    ) -> Response:
        return self.error_response(message, status_code=status.HTTP_401_UNAUTHORIZED, headers=headers)

    def validation_error_response(
        self,
        errors: List[Dict[str, Any]],
        message: str = _("Validation error"),
        headers: Optional[Dict[str, str]] = None,
    ) -> Response:
        return self.error_response(message, errors, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, headers=headers)

    def server_error_response(
        self,
        message: str = _("Internal server error"),
        headers: Optional[Dict[str, str]] = None,
    ) -> Response:
        return self.error_response(message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, headers=headers)