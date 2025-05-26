from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from account.models import User


class UserRegistrationTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('register_api')
        self.valid_data = {
            'email': 'newuser@example.com',
            'password': 'testpass123',
            'user_type': 'customer'
        }

    def test_user_registration_success(self):
        """Test successful user registration"""
        response = self.client.post(self.register_url, self.valid_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.first()
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertEqual(user.user_type, 'customer')

    def test_registration_invalid_user_type(self):
        """Test registration with invalid user type"""
        invalid_data = self.valid_data.copy()
        invalid_data['user_type'] = 'invalid_type'

        response = self.client.post(self.register_url, invalid_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('user_type', [error['field'] for error in response.data['errors']])

    def test_registration_missing_password(self):
        """Test registration with missing password"""
        invalid_data = self.valid_data.copy()
        del invalid_data['password']

        response = self.client.post(self.register_url, invalid_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', [error['field'] for error in response.data['errors']])

    def test_registration_duplicate_email(self):
        """Test registration with duplicate email"""
        User.objects.create_user(
            email='existing@example.com',
            password='testpass123',
            user_type='customer'
        )

        invalid_data = self.valid_data.copy()
        invalid_data['email'] = 'existing@example.com'

        response = self.client.post(self.register_url, invalid_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', [error['field'] for error in response.data['errors']])
