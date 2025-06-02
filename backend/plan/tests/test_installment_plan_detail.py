from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from customer.tests.factories import CustomerUserFactory
from merchant.tests.factories import MerchantUserFactory
from installment.tests.factories import InstallmentPlanFactory
from plan.tests.factories import PlanFactory
from installment.utils.signal_control import disable_installment_creation_signal


class InstallmentPlanDetailAPIViewTest(APITestCase):
    """Test suite for InstallmentPlanDetailAPIView."""

    def setUp(self):
        self.customer = CustomerUserFactory()
        self.other_customer = CustomerUserFactory()
        self.merchant = MerchantUserFactory()
        self.other_merchant = MerchantUserFactory()

        self.merchant.merchant_profile.is_verified = True
        self.merchant.merchant_profile.save()

        self.plan = PlanFactory(merchant=self.merchant)

        with disable_installment_creation_signal():
            self.installment_plan = InstallmentPlanFactory(
                plan=self.plan, customer=self.customer
            )

        self.detail_url = lambda pk: reverse("installment_plan_detail_api", kwargs={"pk": pk})

    def test_customer_can_retrieve_own_installment_plan(self):
        """Test customer can access their own installment plan."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(self.detail_url(self.installment_plan.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["id"], self.installment_plan.pk)

    def test_merchant_can_retrieve_their_template_installment_plan(self):
        """Test merchant can access their template's installment plan."""
        self.client.force_authenticate(user=self.merchant)
        response = self.client.get(self.detail_url(self.installment_plan.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["id"], self.installment_plan.pk)

    def test_forbidden_access_for_other_customer(self):
        """Test access denied for other customers."""
        self.client.force_authenticate(user=self.other_customer)
        response = self.client.get(self.detail_url(self.installment_plan.pk))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_forbidden_access_for_other_merchant(self):
        """Test access denied for other merchants."""
        self.client.force_authenticate(user=self.other_merchant)
        response = self.client.get(self.detail_url(self.installment_plan.pk))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_not_found_for_non_existent_plan(self):
        """Test 404 returned for nonexistent installment plan."""
        self.client.force_authenticate(user=self.customer)
        non_existent_id = self.installment_plan.pk + 999
        response = self.client.get(self.detail_url(non_existent_id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_user_access_denied(self):
        """Test unauthenticated access is denied."""
        response = self.client.get(self.detail_url(self.installment_plan.pk))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
