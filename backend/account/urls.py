from django.urls import path
from account.views import (
    UserRegistrationView,
    CustomTokenObtainPairView,
    CustomTokenRefreshView
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register_api'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair_api'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh_api'),
]