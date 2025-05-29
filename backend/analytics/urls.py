from django.urls import path
from analytics.views import MerchantDashboardAPIView

urlpatterns = [
    path('dashboard/', MerchantDashboardAPIView.as_view(), name='merchant_dashboard_api'),
]
