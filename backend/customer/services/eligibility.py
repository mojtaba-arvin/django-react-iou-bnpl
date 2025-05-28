from customer.models import CustomerProfile


class CustomerEligibilityService:
    @staticmethod
    def get_eligible_profiles():
        """
        Returns customer profiles eligible to join an InstallmentPlan.
        """
        return CustomerProfile.objects.eligible()

    @staticmethod
    def get_eligible_users():
        """
        Returns users of customer profiles eligible to join an InstallmentPlan.
        """
        return CustomerProfile.objects.eligible().values_list('user', flat=True)
