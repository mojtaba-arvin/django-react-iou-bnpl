from django.contrib.auth import get_user_model

from customer.models import CustomerProfile

User = get_user_model()


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

    @staticmethod
    def get_eligible_customers_queryset(email: str = None):
        """
        Returns a User queryset of eligible customers, optionally filtered by
        email substring. Ordered by descending credit_score, then signup date.
        """
        qs = User.objects.filter(
            user_type=User.UserType.CUSTOMER,
            customer_profile__is_active=True,
            customer_profile__score_status=CustomerProfile.ScoreStatus.APPROVED,
        ).select_related('customer_profile') \
         .order_by('-customer_profile__credit_score', 'customer_profile__created_at')

        if email:
            qs = qs.filter(email__icontains=email)

        return qs
