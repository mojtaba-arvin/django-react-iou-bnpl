import factory
from factory.django import DjangoModelFactory
from merchant.tests.factories import MerchantUserFactory
from plan.models import Plan


class PlanFactory(DjangoModelFactory):
    """Factory for creating Plan instances for testing."""

    class Meta:
        model = Plan

    merchant = factory.SubFactory(MerchantUserFactory)
    name = "Default Plan"
    total_amount = 1000.00
    installment_count = 4
    installment_period = 30  # in days
    status = Plan.Status.DRAFT
