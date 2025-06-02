from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import View
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from installment.models import InstallmentPlan

User = get_user_model()


class HasInstallmentPlanPermission(BasePermission):
    """
    Object-level permission to access an InstallmentPlan instance.

    - Merchants can access the installment plan if they are the owner of the template plan.
    - Customers can access the installment plan if they are assigned to it.
    - All other user types are denied access.
    """

    message: str

    def has_object_permission(
        self, request: Request, view: View, obj: InstallmentPlan
    ) -> bool:
        """
        Determine whether the request user has object-level access to the InstallmentPlan.

        Args:
            request (Request): The HTTP request object.
            view (View): The DRF view that is being accessed.
            obj (InstallmentPlan): The InstallmentPlan instance to check access for.

        Returns:
            bool: True if the user has access, False otherwise.
        """
        if request.user.user_type == User.UserType.MERCHANT:
            self.message = str(_("Merchant is not the owner of the associated template plan"))
            return obj.plan.merchant == request.user

        if request.user.user_type == User.UserType.CUSTOMER:
            self.message = str(_("Customer is not assigned to this installment plan"))
            return obj.customer == request.user

        return False

