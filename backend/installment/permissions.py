from rest_framework import permissions

class IsInstallmentCustomer(permissions.BasePermission):
    """
    Custom permission to only allow the customer associated with the installment
    to make a payment.
    """

    def has_object_permission(self, request, view, obj):
        """
        Check if the current user is the customer of the installment.
        """

        # Ensure the user is the customer associated with the installment
        return obj.installment_plan.customer == request.user
