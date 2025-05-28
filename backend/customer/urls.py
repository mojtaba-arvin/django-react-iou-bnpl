from django.urls import path

from customer.views import EligibleCustomerListAPIView

urlpatterns = [
    path('eligible/', EligibleCustomerListAPIView.as_view(), name='eligible_customer_list_api'),
]
