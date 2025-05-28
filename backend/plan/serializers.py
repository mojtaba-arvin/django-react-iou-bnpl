from typing import Any, Dict, List, Optional

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from customer.models import CustomerProfile
from plan.constants import DEFAULT_INSTALLMENT_PERIOD
from installment.models import InstallmentPlan, Installment
from installment.serializers import InstallmentSerializer, InstallmentPlanSerializer
from plan.models import Plan
from plan.services.plan_creator import PlanCreatorService

User = get_user_model()


class PlanSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/retrieving a Plan. Optionally supports assigning a list of customer IDs
    to immediately create associated InstallmentPlan objects for those customers.
    """

    customer_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True,
        help_text=(
            "Optional: List of customer IDs for whom installment plans should be "
            "generated upon plan creation."
        ),
    )

    installment_count = serializers.IntegerField(
        help_text="Number of installments. Example: 4"
    )
    installment_period = serializers.IntegerField(
        required=False,
        default=DEFAULT_INSTALLMENT_PERIOD,
        help_text="Installment interval in days. Example: 30"
    )

    installments = serializers.SerializerMethodField()
    installment_plan = serializers.SerializerMethodField()

    class Meta:
        model = Plan
        fields = [
            'id',
            'name',
            'total_amount',
            'installment_count',
            'installment_period',
            'status',
            'customer_ids',
            'installment_plan',
            'installments',
        ]
        read_only_fields = ['status']  # Status is read-only as all plans are active on creation.

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes the serializer and caches validated customer objects."""
        super().__init__(*args, **kwargs)
        self._validated_customers: Optional[List[User]] = None

    def get_installments(self, plan: Plan) -> List[Dict[str, Any]]:
        """
        Retrieves the installments associated with a plan for the authenticated customer.

        Args:
            plan (Plan): The plan for which installments are fetched.

        Returns:
            List[Dict[str, Any]]: A list of serialized installments for the plan.
        """
        request = self.context['request']
        user = request.user

        if not user.is_authenticated or user.user_type != User.UserType.CUSTOMER:
            return []

        installments = Installment.objects.filter(
            installment_plan__plan=plan,
            installment_plan__customer=user,
        ).order_by('sequence_number')

        return InstallmentSerializer(installments, many=True).data

    def get_installment_plan(self, plan: Plan) -> Dict[str, Any]:
        """
        Retrieves the installment plan associated with a plan for the authenticated customer.

        Args:
            plan (Plan): The plan for which the installment plan is fetched.

        Returns:
            Dict[str, Any]: The serialized installment plan for the customer.
        """
        request = self.context['request']
        user = request.user

        if not user.is_authenticated or user.user_type != User.UserType.CUSTOMER:
            return {}

        installment_plan = InstallmentPlan.objects.get(
            plan=plan,
            customer=user,
        )

        return InstallmentPlanSerializer(installment_plan).data

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates the input data for creating a Plan.

        Args:
            data (Dict[str, Any]): The validated data from the request.

        Returns:
            Dict[str, Any]: The validated data, potentially with modifications.

        Raises:
            ValidationError: If customer IDs are provided and any are ineligible.
        """
        request = self.context['request']

        if request.method.lower() == "post" and request.user.user_type == User.UserType.MERCHANT:
            customer_ids = data.get("customer_ids")
            if customer_ids:
                eligible_customers_qs = User.objects.filter(
                    id__in=customer_ids,
                    user_type=User.UserType.CUSTOMER,
                    customer_profile__score_status=CustomerProfile.ScoreStatus.APPROVED,
                    customer_profile__is_active=True,
                ).select_related("customer_profile")

                eligible_ids = {user.id for user in eligible_customers_qs}
                ineligible_ids = set(customer_ids) - eligible_ids

                if ineligible_ids:
                    raise ValidationError({
                        "customer_ids": _(
                            f"The following customer IDs are not eligible: {sorted(ineligible_ids)}"
                        )
                    })

                # Cache validated customer objects to avoid re-querying
                self._validated_customers = list(eligible_customers_qs)

        return data

    def create(self, validated_data: Dict[str, Any]) -> Plan:
        """
        Creates a Plan instance and associated InstallmentPlan objects, if customer IDs are provided.

        Args:
            validated_data (Dict[str, Any]): The validated data for creating the plan.

        Returns:
            Plan: The newly created plan instance.
        """
        # Use cached customer objects from validate() to avoid re-querying
        customers = self._validated_customers or []

        service = PlanCreatorService(
            merchant=self.context['request'].user,
            name=validated_data['name'],
            total_amount=validated_data['total_amount'],
            installment_count=validated_data['installment_count'],
            installment_period=validated_data.get('installment_period', DEFAULT_INSTALLMENT_PERIOD),
            customers=customers,
        )
        return service.execute()
