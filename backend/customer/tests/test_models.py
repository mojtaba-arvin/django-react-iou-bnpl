from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.test import TestCase
from account.models import User
from customer.constants import CREDIT_SCORE_MAX
from customer.models import CustomerProfile
from customer.signals import create_customer_profile
from customer.tests.factories import CustomerProfileFactory, CustomerUserFactory


class CustomerProfileModelTest(TestCase):
    """
    Test suite for the `CustomerProfile` model.
    """

    def setUp(self) -> None:
        post_save.disconnect(create_customer_profile, sender=User)
        self.customer_user = CustomerUserFactory()

    def tearDown(self) -> None:
        """
        Restore the post-save signal after tests have run.
        """
        post_save.connect(create_customer_profile, sender=User)

    def test_profile_creation(self) -> None:
        """
        Test the creation of a `CustomerProfile`
        """
        profile = CustomerProfile(
            user=self.customer_user,
            credit_score=750
        )
        self.assertEqual(profile.user.email, self.customer_user.email)
        self.assertEqual(profile.credit_score, 750)
        self.assertTrue(profile.is_active)  # Default should be True

    def test_credit_score_validation(self) -> None:
        """
        Test validation for credit score. Ensure an error is raised when
        the credit score exceeds the maximum allowed value.
        """
        profile = CustomerProfile(
            user=self.customer_user,
            credit_score=CREDIT_SCORE_MAX + 100  # Above maximum allowed
        )
        with self.assertRaises(ValidationError):
            profile.full_clean()  # This will trigger field validators

    def test_string_representation(self) -> None:
        profile = CustomerProfileFactory()
        self.assertEqual(str(profile), profile.user.email)

    def test_factory_creation(self) -> None:
        profile = CustomerProfileFactory()
        self.assertIsInstance(profile, CustomerProfile)
        self.assertEqual(profile.user.user_type, User.UserType.CUSTOMER)
