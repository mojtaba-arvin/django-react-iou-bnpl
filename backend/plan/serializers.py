from datetime import date
from typing import Any, Dict, Optional, Union

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator

from plan.constants import DEFAULT_INSTALLMENT_PERIOD, MAX_INSTALLMENT_COUNT, MIN_INSTALLMENT_COUNT, MIN_PLAN_AMOUNT
from installment.models import InstallmentPlan
from installment.serializers import BaseInstallmentSerializer
from plan.models import Plan
from plan.services.plan_creator import PlanCreatorService
from plan.validators import PlanValidator

User = get_user_model()


class ProgressSerializer(serializers.Serializer):
    """Serializer for calculating and representing payment progress metrics.

    Attributes:
        paid: Number of installments already paid.
        total: Total number of installments in the plan.
        percentage: Payment completion percentage (0-100).
        next_due_date: Date of the next upcoming installment.
        days_remaining: Days remaining until next payment is due.
    """

    paid = serializers.IntegerField(help_text="Number of installments paid")
    total = serializers.IntegerField(help_text="Total number of installments")
    percentage = serializers.FloatField(
        help_text="Percentage of installments paid (0-100)"
    )
    next_due_date = serializers.DateField(
        help_text="Next upcoming due date",
        required=False
    )
    days_remaining = serializers.IntegerField(
        help_text="Days remaining until next due date",
        required=False
    )

    def to_representation(self, instance: InstallmentPlan) -> Dict[str, Optional[int]]:
        """Transform the installment plan instance into progress metrics.

        Args:
            instance: The InstallmentPlan instance to calculate progress for.

        Returns:
            Dictionary containing:
                - paid: Count of paid installments
                - total: Total installments
                - percentage: Completion percentage
                - next_due_date: Next due date (if pending installments exist)
                - days_remaining: Days until next payment (if applicable)
        """
        paid = instance.installments.filter(status='paid').count()
        total = instance.installments.count()
        percentage = (paid / total * 100) if total else 0

        next_installment = instance.installments.filter(
            status='pending'
        ).order_by('due_date').first()

        representation = {
            'paid': paid,
            'total': total,
            'percentage': percentage,
        }

        if next_installment:
            representation.update({
                'next_due_date': next_installment.due_date,
                'days_remaining': (next_installment.due_date - timezone.now().date()).days
            })

        return representation


class InstallmentPlanCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating an installment plan (merchant only).
     """

    name = serializers.CharField(
        max_length=128
    )
    total_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(
                MIN_PLAN_AMOUNT,
                message=_('Amount must be ≥ {min} USD.').format(min=MIN_PLAN_AMOUNT)
            )
        ]
    )
    installment_count = serializers.IntegerField(
        help_text="Number of installments. Example: 4",
        max_value=MAX_INSTALLMENT_COUNT,
        min_value=MIN_INSTALLMENT_COUNT,
        error_messages={
            'max_value': _('Maximum number of installments is {max}.').format(max=MAX_INSTALLMENT_COUNT),
            'min_value': _('Minimum number of installments is {min}.').format(min=MIN_INSTALLMENT_COUNT)
        }
    )
    installment_period = serializers.IntegerField(
        required=False,
        default=DEFAULT_INSTALLMENT_PERIOD,
        help_text="Installment interval in days. Example: 30"
    )
    customer_email = serializers.EmailField(
        write_only=True,
        help_text="Customer email for whom installment plan should be created."
    )
    start_date = serializers.DateField(
        required=False,
        default=date.today,
        write_only=True,
        help_text="Start date for the installment plan (defaults to today).Use this format: YYYY-MM-DD"
    )

    class Meta:
        model = InstallmentPlan
        fields = [
            'id',

            # to create a template plan
            'name',
            'total_amount',
            'installment_count',
            'installment_period',

            # to assign installment plan to specific customer
            'customer_email',
            'start_date',
        ]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the serializer.

        Sets up:
        - _validated_customer: Cache for validated customer object
        - validator: PlanValidator instance for validation logic
        """
        super().__init__(*args, **kwargs)
        self._validated_customer: Optional[User] = None
        self.validator = PlanValidator()

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate plan creation data.

        Args:
            data: Input data for plan creation containing:
                - start_date: Optional custom start date (defaults to today)
                - customer_email: Optional customer email

        Returns:
            Validated data dictionary

        Raises:
            ValidationError: If any validation fails including:
                - Invalid start date (in the past)
                - Invalid customer email
        """
        request = self.context['request']

        data, customer = self.validator.validate(data, request)
        # Cache validated the customer object to avoid re-querying
        self._validated_customer = customer

        return data

    def create(self, validated_data: Dict[str, Any]) -> InstallmentPlan:
        """
        Creates a Plan instance and associated InstallmentPlan object by customer_email.

        Args:
            validated_data (Dict[str, Any]): The validated data for creating the plan.

        Returns:
            Plan: The newly created plan instance.
        """
        # Use cached customer objects from validate() to avoid re-querying
        customer = self._validated_customer

        service = PlanCreatorService(
            merchant=self.context['request'].user,
            name=validated_data['name'],
            total_amount=validated_data['total_amount'],
            installment_count=validated_data['installment_count'],
            installment_period=validated_data.get('installment_period', DEFAULT_INSTALLMENT_PERIOD),
            customer=customer,
            start_date=validated_data['start_date'],
            plan_status=Plan.Status.ACTIVE
        )
        return service.execute()


class TemplatePlanSerializer(serializers.ModelSerializer):
    """Serializer for Plan model with merchant information.
    """

    class Meta:
        """Metadata options for TemplatePlanSerializer."""

        model = Plan
        fields = [
            'id',
            'name',
            'total_amount',
            'installment_count',
            'installment_period',
        ]
        read_only_fields = fields


class InstallmentPlanDetailSerializer(serializers.ModelSerializer):
    """Comprehensive serializer for InstallmentPlan with related data.

    Combines:
        - Core installment plan fields
        - Template plan details
        - Payment progress metrics
        - Individual installments
        - Context-sensitive customer information
    """
    progress = ProgressSerializer(
        source='*',
        help_text="Payment progress metrics and calculations"
    )
    template_plan = TemplatePlanSerializer(
        source='plan',
        help_text="Details of the template plan this is based on"
    )
    installments = BaseInstallmentSerializer(many=True, source='ordered_installments')
    customer_email = serializers.SerializerMethodField(
        help_text="Email of the customer (visible to merchants only)"
    )

    class Meta:
        """Metadata options for InstallmentPlanDetailSerializer."""

        model = InstallmentPlan
        fields = [
            'id',
            'start_date',
            'status',
            'customer_email',
            'template_plan',
            'progress',
            'installments',
        ]
        read_only_fields = fields

    def get_customer_email(self, obj: InstallmentPlan) -> Optional[str]:
        """Get customer email if request user is a merchant.

        Args:
            obj: The InstallmentPlan instance being serialized

        Returns:
            str: Customer email if viewer is merchant, None otherwise
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if request.user.user_type == User.UserType.MERCHANT:
                return obj.customer.email
        return None

    def to_representation(self, instance: InstallmentPlan) -> Dict[str, Union[str, int, float, Dict]]:
        """Final representation with context-sensitive field removal.

        Args:
            instance: The InstallmentPlan instance to serialize

        Returns:
            Dictionary containing all serialized fields, with customer_email
            removed if not applicable
        """
        representation = super().to_representation(instance)

        # Remove customer_email field entirely if None
        if representation['customer_email'] is None:
            representation.pop('customer_email', None)

        return representation