from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from customer.tests.factories import CustomerUserFactory
from installment.models import Installment, InstallmentPlan
from installment.utils.signal_control import disable_installment_creation_signal
from merchant.tests.factories import MerchantUserFactory
from plan.models import Plan
from plan.tests.factories import PlanFactory
from installment.tests.factories import InstallmentPlanFactory, InstallmentFactory


class InstallmentPaymentAPITest(APITestCase):
    """Test suite for installment payment functionality.

    Verifies that customers can pay installments, while merchants cannot.
    """

    def setUp(self):
        self.merchant = MerchantUserFactory()
        self.merchant.merchant_profile.is_verified = True
        self.customer = CustomerUserFactory()
        self.plan = PlanFactory(
            merchant=self.merchant,
            status=Plan.Status.ACTIVE
        )

        # Disable installment creation signal during test setup
        with disable_installment_creation_signal():
            self.installment_plan = InstallmentPlanFactory(
                plan=self.plan,
                customer=self.customer
            )

        self.installment = InstallmentFactory(
            installment_plan=self.installment_plan,
            status=Installment.Status.PENDING,
        )

    def test_customer_can_pay_installment(self):
        """Test that a customer can successfully pay an installment."""
        self.client.force_authenticate(user=self.customer)
        url = reverse('installment_pay_api', kwargs={'pk': self.installment.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Refresh the installment to verify the status change
        self.installment.refresh_from_db()
        self.assertEqual(self.installment.status, Installment.Status.PAID)

    def test_merchant_cannot_pay_installment(self):
        """Test that a merchant cannot pay an installment."""
        self.client.force_authenticate(user=self.merchant)
        url = reverse('installment_pay_api', kwargs={'pk': self.installment.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_cannot_pay_already_paid_installment(self):
        """Test that a customer cannot pay an already paid installment."""
        # Mark installment as paid
        self.installment.status = Installment.Status.PAID
        self.installment.save()

        self.client.force_authenticate(user=self.customer)
        url = reverse('installment_pay_api', kwargs={'pk': self.installment.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_customer_cannot_pay_when_installment_plan_is_not_active(self) -> None:
        """Test that a customer cannot pay when the installment plan is not active."""
        self.installment_plan.status = InstallmentPlan.Status.COMPLETED
        self.installment_plan.save()

        self.client.force_authenticate(user=self.customer)
        url = reverse('installment_pay_api', kwargs={'pk': self.installment.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_customer_cannot_pay_installment_when_previous_installments_are_unpaid(self):
        """Test that a customer cannot pay an installment when previous installments are unpaid."""
        # Create previous unpaid installment
        InstallmentFactory(
            installment_plan=self.installment_plan,
            sequence_number=self.installment.sequence_number - 1,
            status=Installment.Status.PENDING,
        )

        self.client.force_authenticate(user=self.customer)
        url = reverse('installment_pay_api', kwargs={'pk': self.installment.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
