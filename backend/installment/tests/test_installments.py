"""Tests for customer installment listing functionality."""
from datetime import date, timedelta
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from customer.tests.factories import CustomerUserFactory
from merchant.tests.factories import MerchantUserFactory
from installment.constants import InstallmentStatusFilters
from installment.models import Installment
from installment.utils.signal_control import disable_installment_creation_signal
from installment.tests.factories import InstallmentPlanFactory, InstallmentFactory
from plan.tests.factories import PlanFactory


class InstallmentListAPIViewTest(APITestCase):
    """Test suite for installment listing functionality."""

    def setUp(self):
        """Set up test data."""
        self.customer = CustomerUserFactory()
        self.merchant = MerchantUserFactory()
        self.merchant.merchant_profile.is_verified = True
        self.merchant.merchant_profile.save()

        self.plan = PlanFactory(merchant=self.merchant, installment_count=3)

        with disable_installment_creation_signal():
            self.installment_plan = InstallmentPlanFactory(
                plan=self.plan, customer=self.customer
            )

        today = date.today()
        self.past_installment = InstallmentFactory(
            installment_plan=self.installment_plan,
            due_date=today - timedelta(days=10),
            status=Installment.Status.PAID,
        )
        self.current_installment = InstallmentFactory(
            installment_plan=self.installment_plan,
            due_date=today,
            status=Installment.Status.PENDING,
        )
        self.next_installment = InstallmentFactory(
            installment_plan=self.installment_plan,
            due_date=today + timedelta(days=10),
            status=Installment.Status.PENDING,
        )

        self.url = reverse("installment_list_api")

    def test_customer_can_view_own_installments(self):
        """Test customer can view their own installments."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 3)

    def test_merchant_cannot_view_customer_installments(self):
        """Test merchant cannot view customer installments."""
        self.client.force_authenticate(user=self.merchant)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_upcoming_installments(self):
        """Test filtering for upcoming installments."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(
            self.url, {"status": InstallmentStatusFilters.UPCOMING}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 2)
        self.assertEqual(response.data["data"][0]["id"], self.current_installment.id)

    def test_filter_past_installments(self):
        """Test filtering for past installments."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(self.url, {"status": InstallmentStatusFilters.PAST})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["id"], self.past_installment.id)

    def test_unauthenticated_access_denied(self):
        """Test unauthenticated users cannot access endpoint."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
