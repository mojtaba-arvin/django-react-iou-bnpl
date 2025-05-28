import pytest
from django.db.models.signals import post_save
from django.test import TestCase

from account.models import User
from merchant.models import MerchantProfile
from merchant.signals import create_merchant_profile
from merchant.tests.factories import MerchantUserFactory, MerchantProfileFactory


@pytest.mark.django_db
class MerchantProfileModelTest(TestCase):
    def setUp(self):
        post_save.disconnect(create_merchant_profile, sender=User)

        # Create a unique user to associate with MerchantProfile for each test
        self.merchant_user = MerchantUserFactory()

    def tearDown(self):
        post_save.connect(create_merchant_profile, sender=User)

    def test_profile_factory(self):
        profile = MerchantProfileFactory(user=self.merchant_user)
        self.assertIsNotNone(profile.business_name)
        self.assertIsNotNone(profile.business_registration_number)

    def test_profile_creation(self):
        """Test merchant profile can be created"""
        profile = MerchantProfileFactory(
            user=self.merchant_user,
            business_name='Test Business',
            business_registration_number='1234567890'
        )

        self.assertEqual(profile.user.email, self.merchant_user.email)
        self.assertEqual(profile.business_name, 'Test Business')
        self.assertFalse(profile.is_verified)

    def test_string_representation(self):
        """Test __str__ returns business name"""
        profile = MerchantProfileFactory(business_name="Awesome Business")
        self.assertEqual(str(profile), "Awesome Business")

    def test_factory_creation(self):
        """Test FactoryBoy creates valid merchant profile"""
        profile = MerchantProfileFactory()
        self.assertIsInstance(profile, MerchantProfile)
        self.assertEqual(profile.user.user_type, User.UserType.MERCHANT)