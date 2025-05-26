from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from account.models import User


class JWTAuthTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            user_type=User.UserType.CUSTOMER
        )
        self.login_url = reverse('token_obtain_pair_api')

    def test_jwt_login_success(self):
        """Test successful JWT token generation"""
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data['data'])
        self.assertIn('refresh', response.data['data'])

    def test_jwt_login_invalid_credentials(self):
        """Test JWT login with invalid credentials"""
        data = {
            'email': 'test@example.com',
            'password': 'wrongpass'
        }
        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_jwt_token_contains_user_type(self):
        """Test JWT token contains custom user_type claim"""
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify token contains user_type in payload
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken(response.data['data']['access'])
        self.assertEqual(token['user_type'], 'customer')