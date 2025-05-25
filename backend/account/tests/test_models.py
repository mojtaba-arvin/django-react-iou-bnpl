from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UserModelTests(TestCase):
    def test_create_user(self):
        """Test creating a new user"""
        user_model = get_user_model()
        email = 'test@example.com'
        password = 'testpass123'
        user_type = User.UserType.CUSTOMER
        user = user_model.objects.create_user(
            email=email,
            password=password,
            user_type=user_type
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertEqual(user.user_type, user_type)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_create_superuser(self):
        """Test creating a new superuser"""
        user = User.objects.create_superuser(
            email='admin@example.com',
            password='testpass123'
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)
        self.assertEqual(user.user_type, User.UserType.MERCHANT)

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email=None,
                password='test123',
                user_type=User.UserType.CUSTOMER
            )

    def test_user_type_choices(self):
        """Test user_type choices are correct"""
        self.assertEqual(User.UserType.CUSTOMER, 'customer')
        self.assertEqual(User.UserType.MERCHANT, 'merchant')
        # Ensure choices tuple contains expected pairs
        choices = dict(User.UserType.choices)
        self.assertIn('customer', choices)
        self.assertIn('merchant', choices)

    def test_user_str_representation(self):
        """Test user string representation"""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            user_type=User.UserType.MERCHANT
        )
        self.assertEqual(str(user), 'test@example.com (merchant)')
