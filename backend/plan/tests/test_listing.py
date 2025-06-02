from django.urls import reverse
from rest_framework.test import APITestCase
from customer.tests.factories import CustomerUserFactory
from installment.models import InstallmentPlan, Installment
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

        self.url = reverse('installment_plan_list_create_api')

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

    def test_email_in_serialized_data_for_merchants(self):
        """Verify customer_email is included for merchants."""
        self.client.force_authenticate(user=self.merchant1)
        response = self.client.get(self.url)
        self.assertEqual(response.data['data'][0]['customer_email'], self.customer.email)

    def test_email_not_in_serialized_data_for_customers(self):
        """Test that customer_email field is completely absent for customers."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(self.url)
        first_plan = response.data['data'][0]

        # Field should be completely removed, not just None
        self.assertNotIn('customer_email', first_plan)

    def test_pagination(self):
        """Test that pagination works correctly."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(f"{self.url}?page=1&page_size=2")
        self.assertEqual(len(response.data['data']), 2)
        self.assertEqual(response.data['pagination']['total_pages'], 3)
        self.assertEqual(response.data['pagination']['current_page'], 1)

    def test_only_active_installment_plans_shown(self):
        """Test that only active installment plans are shown in the list."""

        plan_template = PlanFactory(
            merchant=self.merchant1,
            status=Plan.Status.ACTIVE
        )
        installment_plan = InstallmentPlanFactory(
            plan=plan_template,
            customer=self.customer,
            status=InstallmentPlan.Status.ACTIVE
        )
        installment_plan.status = InstallmentPlan.Status.DEFAULTED
        installment_plan.save()

        self.client.force_authenticate(user=self.customer)
        response = self.client.get(self.url)
        self.assertEqual(response.data['pagination']['total_items'], 5)  # Only original active plans

    def test_progress_serializer_calculation(self):
        """Test that progress serializer calculates correctly."""
        # Get a plan with installments
        plan = self.plans_merchant1[0]
        installment_plan = InstallmentPlan.objects.get(plan=plan)

        # Pay first installment
        first_installment = installment_plan.installments.first()
        first_installment.status = Installment.Status.PAID
        first_installment.save()

        self.client.force_authenticate(user=self.customer)
        response = self.client.get(self.url)

        # Find our plan in the response
        response_plan = next(
            p for p in response.data['data']
            if p['id'] == installment_plan.id
        )

        self.assertEqual(response_plan['progress']['paid'], 1)
        self.assertEqual(response_plan['progress']['total'], 4)  # Assuming default count is 4
        self.assertAlmostEqual(response_plan['progress']['percentage'], 25.0)

    def test_template_plan_serialization(self):
        """Test that template plan data is properly serialized."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(self.url)
        first_plan = response.data['data'][0]

        self.assertIn('template_plan', first_plan)
        self.assertEqual(first_plan['template_plan']['name'], self.plans_merchant1[0].name)
        self.assertEqual(str(first_plan['template_plan']['total_amount']), str(self.plans_merchant1[0].total_amount))

    def test_installments_ordering(self):
        """Test that installments are ordered by due date."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(self.url)
        first_plan = response.data['data'][0]

        # Check installments are in order
        due_dates = [i['due_date'] for i in first_plan['installments']]
        self.assertEqual(due_dates, sorted(due_dates))
