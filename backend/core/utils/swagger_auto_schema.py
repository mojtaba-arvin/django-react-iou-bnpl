from drf_yasg.inspectors import SwaggerAutoSchema
from typing import List, Optional, Tuple


class CustomAutoSchema(SwaggerAutoSchema):
    def get_tags(self, operation_keys: Optional[Tuple[str, ...]] = None) -> List[str]:
        """
        Override this to customize tag generation from operation keys.

        Args:
            operation_keys (Optional[Tuple[str]]): A tuple of keys describing the
                operation hierarchy (e.g., ('auth', 'login')). Defaults to an empty tuple.

        Returns:
            List[str]: A list of tags associated with the operation.
        """
        if operation_keys is None:
            operation_keys = ()

        if 'auth' in operation_keys or 'token' in operation_keys:
            return ['Authentication']

        if 'register' in operation_keys:
            return ['Registration']

        # Default behavior for other endpoints
        return super().get_tags(operation_keys)
