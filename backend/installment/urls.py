from django.urls import path
from installment.views import InstallmentPaymentAPIView, InstallmentListAPIView

urlpatterns = [
    path('', InstallmentListAPIView.as_view(), name='installment_list_api'),
    path('<int:pk>/pay/', InstallmentPaymentAPIView.as_view(), name='installment_pay_api'),
]
