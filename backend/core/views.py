from typing import Any
from rest_framework import generics
from rest_framework.exceptions import NotFound
from django.utils.translation import gettext_lazy as _


class CheckObjectPermissionAPIView(generics.GenericAPIView):
    """
    An abstract APIView that provides a method to fetch an object and
    automatically checks object-level permissions.

    Use this as a base class when you want to centralize permission checks
    for object retrieval.
    """

    custom_not_found_message = str(_("Not found"))  # overwrite it in view

    def get_object_with_permissions(self, **kwargs: Any) -> Any:
        """
        Retrieve an object using the view's queryset and check object-level permissions.

        Args:
            **kwargs: Lookup fields for retrieving the object.

        Returns:
            The object instance if found and permissions pass.

        Raises:
            NotFound: If the object is not found.
            PermissionDenied: If object-level permissions fail.
        """
        try:
            obj = self.get_queryset().get(**kwargs)
        except self.get_queryset().model.DoesNotExist:
            raise NotFound(self.custom_not_found_message)
        self.check_object_permissions(self.request, obj)
        return obj

