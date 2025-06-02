from django.urls import reverse
from django.db.models.signals import post_save
from rest_framework import status
from rest_framework.test import APITestCase
from account.models import User
from customer.models import CustomerProfile
from customer.signals import create_customer_profile
from customer.tests.factories import CustomerProfileFactory, CustomerUserFactory
from merchant.tests.factories import MerchantUserFactory


class CustomerListingAPITest(APITestCase):
    """
    Integration tests for the eligible customer listing API endpoint.
    Ensures only eligible customers are listed and proper access control is enforced.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Disconnects the automatic creation of customer profiles during test class setup.
        """
        super().setUpClass()
        post_save.disconnect(create_customer_profile, sender=User)

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Reconnects the customer profile creation signal after tests are done.
        """
        post_save.connect(create_customer_profile, sender=User)
        super().tearDownClass()

    def setUp(self) -> None:
        """
        Creates a merchant and a mix of eligible and ineligible customer profiles.
        """
        self.merchant = MerchantUserFactory()

        # Eligible customers
        CustomerProfileFactory.create_batch(
            2,
            score_status=CustomerProfile.ScoreStatus.APPROVED,
            is_active=True,
            credit_score=700
        )

        # Ineligible customers
        CustomerProfileFactory(
            score_status=CustomerProfile.ScoreStatus.PENDING,
            is_active=True,
            credit_score=500
        )
        CustomerProfileFactory(
            score_status=CustomerProfile.ScoreStatus.REJECTED,
            is_active=True,
            credit_score=700
        )
        CustomerProfileFactory(
            score_status=CustomerProfile.ScoreStatus.APPROVED,
            is_active=False,
            credit_score=700
        )

        self.url: str = reverse('eligible_customer_list_api')

    def test_merchant_sees_only_eligible_customers(self) -> None:
        """
        Merchant should see only customers who are:
        - Approved
        - Active
        """
        self.client.force_authenticate(self.merchant)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_count = CustomerProfile.objects.filter(
            score_status=CustomerProfile.ScoreStatus.APPROVED,
            is_active=True
        ).count()

        data = response.data['data']
        self.assertEqual(len(data), expected_count)
        self.assertEqual(response.data['pagination']['total_items'], expected_count)

        for item in data:
            self.assertTrue(item['is_active'])
            self.assertEqual(item['score_status'], CustomerProfile.ScoreStatus.APPROVED)

    def test_customer_cannot_access(self) -> None:
        """
        A customer user should not be allowed to access the eligible customer list.
        """
        customer = CustomerUserFactory()
        self.client.force_authenticate(customer)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_pagination_works_for_merchant(self) -> None:
        """
        Ensure pagination data is correctly returned and functional for merchants.
        """
        self.client.force_authenticate(self.merchant)
        expected_count = CustomerProfile.objects.filter(
            score_status=CustomerProfile.ScoreStatus.APPROVED,
            is_active=True
        ).count()

        response = self.client.get(f"{self.url}?page=1&page_size=1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['pagination']['total_items'], expected_count)
