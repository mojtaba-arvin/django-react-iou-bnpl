"""Serializers for installment related models."""
from typing import Optional

from rest_framework import serializers

from installment.constants import InstallmentStatusFilters
from installment.models import Installment, InstallmentPlan
from installment.services.retrieval import InstallmentRetrievalService


class BaseInstallmentSerializer(serializers.ModelSerializer):
    """Serializer for an Installment model."""

    class Meta:
        model = Installment
        fields = [
            "id",
            "amount",
            "due_date",
            "status",
            "sequence_number",
            "paid_at",
        ]

        read_only_fields = fields


class InstallmentFilterSerializer(serializers.Serializer):
    """Serializer for validating installment filter parameters."""

    status = serializers.ChoiceField(
        choices=InstallmentStatusFilters.CHOICES,
        required=False,
        allow_null=True,
        help_text=InstallmentStatusFilters.get_help_text(),
    )


class CustomerFacingInstallmentSerializer(BaseInstallmentSerializer):
    """Serializer for listing installments along
    with payment eligibility flag, subscription and template plan details.
    """

    # Fields related to InstallmentPlan (subscription)
    subscription_id: serializers.SerializerMethodField = serializers.SerializerMethodField()

    # Fields related to Plan (template plan)
    template_plan_id: serializers.SerializerMethodField = serializers.SerializerMethodField()
    template_plan_name: serializers.SerializerMethodField = serializers.SerializerMethodField()

    # As an annotated Field
    is_payable = serializers.SerializerMethodField()

    class Meta(BaseInstallmentSerializer.Meta):
        fields = BaseInstallmentSerializer.Meta.fields + [
            "subscription_id",
            "template_plan_id",
            "template_plan_name",
            "is_payable",
        ]
        read_only_fields = fields

    @staticmethod
    def get_subscription_id(obj: Installment) -> int:
        """Retrieve the ID of the InstallmentPlan (subscription) for this installment.
        """
        return obj.installment_plan.id

    @staticmethod
    def get_template_plan_id(obj: Installment) -> int:
        """Retrieve the ID of the template Plan.
        """
        return obj.installment_plan.plan.id

    @staticmethod
    def get_template_plan_name(obj: Installment) -> Optional[str]:
        """Retrieve the name of the template Plan.
        """
        return obj.installment_plan.plan.name

    @staticmethod
    def get_is_payable(obj: Installment) -> bool:
        """
        Calculate payment eligibility based on business rules.
        Uses pre-annotated value if available, otherwise computes dynamically.
        """

        # If it's already annotated, use it
        if hasattr(obj, 'is_payable'):
            return obj.is_payable

        # Fallback calculation if isn't annotated
        service = InstallmentRetrievalService(customer=obj.installment_plan.customer)
        return service.validate_installment_payment(obj)
