from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from customer.tests.factories import CustomerUserFactory
from merchant.tests.factories import MerchantUserFactory
from plan.models import Plan


class PlanCreationAPITest(APITestCase):
    """Test suite for plan creation via the Plan API."""

    def setUp(self):
        self.merchant = MerchantUserFactory()
        self.merchant.merchant_profile.is_verified = True
        self.customer = CustomerUserFactory()
        self.client.force_authenticate(user=self.merchant)
        self.url = reverse('plan_list_create_api')

    def test_merchant_can_create_plan(self) -> None:
        """Test that a verified merchant can successfully create a plan."""
        data = {
            'name': '4-Payment Plan',
            'total_amount': 1000.00,
            'installment_count': 4,
            'installment_period': 30
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Plan.objects.count(), 1)
        self.assertEqual(Plan.objects.first().merchant, self.merchant)

    def test_customer_cannot_create_plan(self):
        """Test that a customer user cannot create a plan (permission denied)."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
