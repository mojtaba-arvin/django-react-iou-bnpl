from django.contrib.auth import get_user_model

from customer.models import CustomerProfile

User = get_user_model()

def get_eligible_customers_for_merchant():
    """
    Returns queryset of eligible customers.
    """
    return User.objects.filter(
        user_type=User.UserType.CUSTOMER,
        customer_profile__is_active=True,
        customer_profile__score_status=CustomerProfile.ScoreStatus.APPROVED
    ).select_related('customer_profile') \
     .order_by('-customer_profile__credit_score', 'customer_profile__created_at')