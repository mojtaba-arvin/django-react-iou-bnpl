from django.urls import path
from installment.views import InstallmentPaymentAPIView

urlpatterns = [
    path('<int:pk>/pay/', InstallmentPaymentAPIView.as_view(), name='installment_pay_api'),
]
