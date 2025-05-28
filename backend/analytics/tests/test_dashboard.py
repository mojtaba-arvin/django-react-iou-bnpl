from django.test import TransactionTestCase
from django.urls import reverse
from rest_framework.test import APIClient
from customer.tests.factories import CustomerUserFactory
from installment.models import Installment
from installment.utils.signal_control import disable_installment_creation_signal
from merchant.tests.factories import MerchantUserFactory
from plan.tests.factories import PlanFactory
from installment.tests.factories import InstallmentPlanFactory, InstallmentFactory


class MerchantDashboardTests(TransactionTestCase):
    """Tests for the merchant dashboard API"""

    def setUp(self) -> None:
        self.merchant_dashboard_url = reverse('merchant_dashboard_api')
        self.client = APIClient()

        # Create test users
        self.merchant = MerchantUserFactory()
        self.merchant.merchant_profile.is_verified = True
        self.customer = CustomerUserFactory()

        # Create a plan and install installments with different statuses
        plan = PlanFactory(merchant=self.merchant)

        with disable_installment_creation_signal():
            installment_plan = InstallmentPlanFactory(
                plan=plan,
                customer=self.customer
            )

        # Create paid installments
        InstallmentFactory.create_batch(
            2,
            installment_plan=installment_plan,
            status=Installment.Status.PAID,
            amount=250.00
        )

        # Create pending installments
        InstallmentFactory.create_batch(
            1,
            installment_plan=installment_plan,
            status=Installment.Status.PENDING,
            amount=250.00
        )

        # Create late installments
        InstallmentFactory.create_batch(
            1,
            installment_plan=installment_plan,
            status=Installment.Status.LATE,
            amount=250.00
        )

    def test_merchant_dashboard_metrics(self) -> None:
        """
        Test that the merchant dashboard API returns correct metrics.
        """
        self.client.force_authenticate(user=self.merchant)
        response = self.client.get(self.merchant_dashboard_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['total_revenue'], 500.00)
        self.assertEqual(response.data['data']['success_rate'], 50.0)
        self.assertEqual(response.data['data']['overdue_count'], 1)

    def test_customer_cannot_access_dashboard(self) -> None:
        """
        Test that a customer cannot access the merchant dashboard.
        """
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(self.merchant_dashboard_url)
        self.assertEqual(response.status_code, 403)
