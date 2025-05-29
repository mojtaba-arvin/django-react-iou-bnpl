from rest_framework.exceptions import APIException
from rest_framework import status
from typing import Optional, List, Dict, Any


class BusinessException(APIException):
    """
    Base class for all business exceptions. Carries:
      - message: a human-readable message.
      - status_code: HTTP status for the response.
      - default_code: an internal error code.
      - errors: a list of error objects for granular error info.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "A business error occurred"
    default_code = "business_error"

    def __init__(
        self,
        message: Optional[str] = None,
        code: Optional[str] = None,
        errors: Optional[List[Dict[str, Any]]] = None,
        status_code: Optional[int] = None,
    ):
        # Set detail message
        detail = message or self.default_detail
        # Allow overriding the HTTP status code
        if status_code is not None:
            self.status_code = status_code
        # Store a structured list of error entries
        # Each entry: { code: int, message: str, field: Optional[str] }
        self.errors: List[Dict[str, Any]] = errors or []

        super().__init__(detail, code)

