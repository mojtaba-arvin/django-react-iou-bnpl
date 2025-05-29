from django.test import TestCase
from customer.tests.factories import CustomerUserFactory
from merchant.tests.factories import MerchantUserFactory
from installment.tests.factories import InstallmentPlanFactory
from plan.tests.factories import PlanFactory
from installment.models import InstallmentPlan


class InstallmentModelTest(TestCase):
    """Test cases for installment models."""

    def setUp(self) -> None:
        self.merchant = MerchantUserFactory(
            email='merchant@example.com'
        )
        self.merchant.merchant_profile.is_verified = True
        self.customer = CustomerUserFactory(
            email='customer@example.com',
        )
        self.plan = PlanFactory(
            merchant=self.merchant,
            name="Test Plan",
            total_amount=1000.00,
            installment_count=4,
            installment_period=30
        )

    def test_installment_plan_creation(self) -> None:
        """Test that an installment plan can be created."""
        installment_plan = InstallmentPlan.objects.create(
            plan=self.plan,
            customer=self.customer
        )
        self.assertEqual(installment_plan.plan.name, "Test Plan")
        self.assertEqual(installment_plan.customer.email, 'customer@example.com')

    def test_installment_auto_creation(self) -> None:
        """Test that installments are automatically created."""
        installment_plan = InstallmentPlanFactory(
            plan__total_amount=1000,
            plan__installment_count=4
        )
        self.assertEqual(installment_plan.installments.count(), 4)
        self.assertEqual(installment_plan.installments.first().amount, 250.00)
