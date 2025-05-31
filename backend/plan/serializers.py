from datetime import date
from typing import Any, Dict, List, Optional

from django.contrib.auth import get_user_model
from rest_framework import serializers

from plan.constants import DEFAULT_INSTALLMENT_PERIOD
from installment.models import InstallmentPlan, Installment
from installment.serializers import InstallmentSerializer, InstallmentPlanSerializer
from plan.models import Plan
from plan.services.plan_creator import PlanCreatorService
from plan.validators import PlanValidator

User = get_user_model()


class PlanSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and retrieving payment Plans.

    Supports creating installment plans for customers either by providing:
    - A single customer email (customer_email)
    - A list of customer IDs (customer_ids)

    Also allows setting a custom start date for the installment plan.
    """

    installment_count = serializers.IntegerField(
        help_text="Number of installments. Example: 4"
    )
    installment_period = serializers.IntegerField(
        required=False,
        default=DEFAULT_INSTALLMENT_PERIOD,
        help_text="Installment interval in days. Example: 30"
    )

    # write_only fields
    start_date = serializers.DateField(
        required=False,
        default=date.today,
        write_only=True,
        help_text="Start date for the installment plan (defaults to today).Use this format: YYYY-MM-DD"
    )
    customer_email = serializers.EmailField(
        required=False,
        write_only=True,
        help_text="Optional: Customer email for whom installment plan should be created."
    )
    customer_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True,
        help_text=(
            "Optional: List of customer IDs for whom installment plans should be "
            "generated upon plan creation."
        ),
    )

    # read-only fields
    installments = serializers.SerializerMethodField()
    installment_plan = serializers.SerializerMethodField()

    class Meta:
        model = Plan
        fields = [
            'name',
            'total_amount',
            'installment_count',
            'installment_period',

            # read-only fields
            'id',
            'status',
            'installment_plan',
            'installments',

            # write_only fields
            'start_date',
            'customer_email',
            'customer_ids',
        ]
        read_only_fields = ['status']  # Status is read-only as all plans are active on creation.

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the serializer.

        Sets up:
        - _validated_customers: Cache for validated customer objects
        - validator: PlanValidator instance for validation logic
        """
        super().__init__(*args, **kwargs)
        self._validated_customers: Optional[List[User]] = None
        self.validator = PlanValidator()

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
        """Validate plan creation data.

        Args:
            data: Input data for plan creation containing:
                - start_date: Optional custom start date (defaults to today)
                - customer_email: Optional customer email
                - customer_ids: Optional list of customer IDs

        Returns:
            Validated data dictionary

        Raises:
            ValidationError: If any validation fails including:
                - Invalid start date (in the past)
                - Both customer_ids and customer_email provided
                - Invalid customer IDs or email
        """
        request = self.context['request']

        if request.method.lower() == "post" and request.user.user_type == User.UserType.MERCHANT:

            data, customers = self.validator.validate(data, request)
            # Cache validated customer objects to avoid re-querying
            self._validated_customers = customers

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
            start_date=validated_data['start_date']
        )
        return service.execute()
