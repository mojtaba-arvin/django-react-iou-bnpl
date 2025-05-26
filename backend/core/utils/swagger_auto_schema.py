from drf_yasg.inspectors import SwaggerAutoSchema
from typing import List, Optional


class CustomAutoSchema(SwaggerAutoSchema):

    def get_tags(self, operation_keys: Optional[List[str]] = None) -> List[str]:
        """
        Override this to customize tag generation from operation keys.

        Args:
            operation_keys: List of keys describing the operation hierarchy
                          (e.g., ['auth', 'login'])

        Returns:
            List of tags for the operation
        """
        if operation_keys is None:
            operation_keys = []

        if 'register' in operation_keys:
            return ['Registration']

        # Default behavior for other endpoints
        return super().get_tags(operation_keys)
