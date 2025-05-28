def get_plans_for_user(user):
    """
    Retrieves plans for a given user based on their user type (merchant or customer).

    Args:
        user (User): The user for whom to retrieve the plans.

    Returns:
        QuerySet: A queryset of plans that belong to the user (merchant) or have been assigned to them (customer).
    """
    # Import here to avoid circular imports
    from plan.models import Plan
    from installment.models import InstallmentPlan

    if user.user_type == user.UserType.MERCHANT:
        # If the user is a merchant, return all plans associated with them
        return Plan.objects.filter(merchant=user)

    # If the user is a customer, return only active and completed plans assigned to them
    return Plan.objects.filter(
        status=Plan.Status.ACTIVE,
        installment_plans__customer=user,
        installment_plans__status__in=[
            InstallmentPlan.Status.ACTIVE,
            InstallmentPlan.Status.COMPLETED  # To include historical plans
        ]
    ).distinct()
