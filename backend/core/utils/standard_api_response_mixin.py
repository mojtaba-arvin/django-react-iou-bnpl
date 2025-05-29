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
            success: Boolean indicating if the request was successful.
            message: Human-readable message describing the result.
            data: Main payload of the response (for successful requests).
            errors: List of error details (for failed requests).
            status_code: HTTP status code (default is 200 OK).
            pagination: Pagination metadata (for paginated responses).
            headers: Optional dict of HTTP headers to include in the response.

        Returns:
            DRF Response object with standardized format and headers.
        """
        response_data: Dict[str, Any] = {
            "success": success,
            "message": message,
            "data": data or {},
            "errors": errors or [],
        }

        if pagination:
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

    def get_paginated_success_response(
            self,
            data: List[Dict[str, Any]],
            message: str = str(_("Operation completed successfully"))
    ) -> Response:
        """
        Return a success response for paginated data.
        Uses DRF's pagination attributes set on the view.
        """
        if not hasattr(self, 'paginator') or not hasattr(self.paginator, 'page'):
            raise AttributeError(
                f"{self.__class__.__name__} must be used with a paginator to call get_paginated_success_response()."
            )

        page_obj = self.paginator.page

        pagination_data = {
            "total_items": page_obj.paginator.count,
            "total_pages": page_obj.paginator.num_pages,
            "current_page": page_obj.number,
            "page_size": self.paginator.get_page_size(self.request),
            "next": self.paginator.get_next_link(),
            "previous": self.paginator.get_previous_link(),
        }

        return self.success_response(
            message=message,
            data=data,
            pagination=pagination_data,
        )
