from datetime import date, timedelta

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from customer.models import CustomerProfile
from customer.tests.factories import CustomerUserFactory
from installment.models import InstallmentPlan
from merchant.tests.factories import MerchantUserFactory


class PlanCreationAPITest(APITestCase):
    """Test suite for plan creation via the Plan API."""

    def setUp(self):
        self.merchant = MerchantUserFactory()
        self.merchant.merchant_profile.is_verified = True
        self.merchant.merchant_profile.save()

        self.customer = CustomerUserFactory()
        self.customer.customer_profile.score_status = CustomerProfile.ScoreStatus.APPROVED
        self.customer.customer_profile.save()

        self.client.force_authenticate(user=self.merchant)
        self.url = reverse('installment_plan_list_create_api')
        self.base_data: dict[str, str | float | int] = {
            'name': '4-Payment Plan',
            'total_amount': 1000.00,
            'installment_count': 4,
            'installment_period': 30
        }

    def test_merchant_can_create_plan(self):
        """Test that a verified merchant can successfully create a plan."""
        data = self.base_data.copy()
        data.update({
            'customer_email': self.customer.email,
        })
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(InstallmentPlan.objects.count(), 1)
        self.assertEqual(InstallmentPlan.objects.first().customer, self.customer)

    def test_customer_cannot_create_plan(self):
        """Test that a customer user cannot create a plan (permission denied)."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('User account is not a Merchant.',
                      [error['message'] for error in response.data['errors']])

    def test_create_plan_with_start_date(self):
        """Test creating a plan with custom start date."""
        future_date = date.today() + timedelta(days=7)
        data = self.base_data.copy()
        data.update({
            'customer_email': self.customer.email,
            'start_date': future_date.isoformat(),
        })
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            InstallmentPlan.objects.first().start_date,
            future_date
        )

    def test_cannot_use_past_start_date(self):
        """Test that start date cannot be in the past."""
        past_date = date.today() - timedelta(days=1)
        data = self.base_data.copy()
        data.update({
            'customer_email': self.customer.email,
            'start_date': past_date.isoformat(),
        })
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('start_date',
                      [error['field'] for error in response.data['errors']])

    def test_invalid_customer_email(self):
        """Test with invalid customer email."""
        data = self.base_data.copy()
        data.update({
            'customer_email': 'invalid@example.com',
        })
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('customer_email',
                      [error['field'] for error in response.data['errors']])

    def test_unverified_merchant_cannot_create_plan(self):
        """Test that unverified merchants cannot create plans."""
        unverified_merchant = MerchantUserFactory()
        unverified_merchant.merchant_profile.is_verified = False
        unverified_merchant.merchant_profile.save()

        self.client.force_authenticate(user=unverified_merchant)
        response = self.client.post(self.url, self.base_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data['errors'][0]['message'],
            'Merchant is not verified.'
        )

    def test_default_start_date_is_today(self):
        """Test that start_date defaults to today when not provided."""
        data = self.base_data.copy()
        data.update({
            'customer_email': self.customer.email,
        })
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            InstallmentPlan.objects.first().start_date,
            date.today()
        )

    def test_default_installment_period(self):
        """Test that installment_period defaults to DEFAULT_INSTALLMENT_PERIOD."""
        data = self.base_data.copy()
        data.pop('installment_period')  # Remove to test default
        data.update({
            'customer_email': self.customer.email,
        })
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            InstallmentPlan.objects.first().plan.installment_period,
            30  # DEFAULT_INSTALLMENT_PERIOD
        )

    def test_invalid_installment_count(self):
        """Test validation for installment_count values."""
        invalid_values = [0, -1, 1.5, "0", "invalid"]
        for value in invalid_values:
            data = self.base_data.copy()
            data['installment_count'] = value
            data['customer_email'] = self.customer.email
            response = self.client.post(self.url, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('installment_count',
                          [error['field'] for error in response.data['errors']])

    def test_invalid_total_amount(self):
        """Test validation for total_amount values."""
        invalid_values = [0, -1, "0", "invalid"]
        for value in invalid_values:
            data = self.base_data.copy()
            data['total_amount'] = value
            data['customer_email'] = self.customer.email
            response = self.client.post(self.url, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('total_amount',
                          [error['field'] for error in response.data['errors']])
