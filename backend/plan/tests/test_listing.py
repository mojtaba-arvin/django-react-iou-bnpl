from django.urls import reverse
from rest_framework.test import APITestCase
from customer.tests.factories import CustomerUserFactory
from installment.models import InstallmentPlan
from installment.tests.factories import InstallmentPlanFactory
from merchant.tests.factories import MerchantUserFactory
from plan.models import Plan
from plan.tests.factories import PlanFactory


class PlanListingAPITest(APITestCase):
    """Test suite for listing plans and verifying permissions."""

    def setUp(self):
        self.customer = CustomerUserFactory()
        self.merchant1 = MerchantUserFactory()
        self.merchant2 = MerchantUserFactory()

        # Create plans for each merchant
        self.plans_merchant1 = PlanFactory.create_batch(3, merchant=self.merchant1, status=Plan.Status.ACTIVE)
        self.plans_merchant2 = PlanFactory.create_batch(2, merchant=self.merchant2, status=Plan.Status.ACTIVE)

        # Assign all plans to the customer via InstallmentPlan
        for plan in self.plans_merchant1 + self.plans_merchant2:
            InstallmentPlanFactory(
                plan=plan,
                customer=self.customer,
                status=InstallmentPlan.Status.ACTIVE
            )

        self.url = reverse('plan_list_create_api')

    def test_merchant_sees_only_their_plans(self):
        """Test that a merchant can see only their own active plans."""
        self.client.force_authenticate(user=self.merchant1)
        response = self.client.get(self.url)
        self.assertEqual(len(response.data['data']), 3)
        self.assertEqual(response.data['pagination']['total_items'], 3)

    def test_customer_sees_assigned_plans(self):
        """Test that a customer can see all assigned plans."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(self.url)
        self.assertEqual(len(response.data['data']), 5)
        self.assertEqual(response.data['pagination']['total_items'], 5)
