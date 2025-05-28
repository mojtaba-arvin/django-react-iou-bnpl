from django.shortcuts import get_object_or_404
from rest_framework import generics
from typing import Any


class CheckObjectPermissionAPIView(generics.GenericAPIView):
    """
    An abstract APIView that provides a method to fetch an object and
    automatically checks object-level permissions.

    Use this as a base class when you want to centralize permission checks
    for object retrieval.
    """

    def get_object_with_permissions(self, **kwargs: Any) -> Any:
        """
        Retrieve an object using the view's queryset and check object-level permissions.

        Args:
            **kwargs: Lookup fields for retrieving the object.

        Returns:
            The object instance if found and permissions pass.

        Raises:
            Http404: If the object is not found.
            PermissionDenied: If object-level permissions fail.
        """
        obj = get_object_or_404(self.get_queryset(), **kwargs)
        self.check_object_permissions(self.request, obj)
        return obj

