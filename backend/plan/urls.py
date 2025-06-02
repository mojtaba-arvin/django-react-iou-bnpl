from django.urls import path
from plan.views import InstallmentPlanListCreateAPIView, InstallmentPlanDetailAPIView

urlpatterns = [
    path('', InstallmentPlanListCreateAPIView.as_view(), name='installment_plan_list_create_api'),
    path('<int:pk>/', InstallmentPlanDetailAPIView.as_view(), name='installment_plan_detail_api'),
]
