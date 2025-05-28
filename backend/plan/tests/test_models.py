from django.test import TestCase
from merchant.tests.factories import MerchantUserFactory
from plan.models import Plan
from plan.tests.factories import PlanFactory


class PlanModelTest(TestCase):
    """Test cases for the Plan model functionality."""

    def setUp(self) -> None:
        """Set up a merchant user and ensure the profile is verified."""
        self.merchant = MerchantUserFactory(email='merchant@example.com')
        self.merchant.merchant_profile.is_verified = True

    def test_plan_creation(self) -> None:
        """Test that a merchant can create a payment plan template."""
        plan = PlanFactory(merchant=self.merchant)
        self.assertEqual(plan.merchant.email, 'merchant@example.com')
        self.assertEqual(plan.status, Plan.Status.DRAFT)

    def test_string_representation(self) -> None:
        """Test that the string representation of the plan is correct."""
        plan = PlanFactory(name="Test Plan")
        self.assertEqual(str(plan), "Test Plan")
