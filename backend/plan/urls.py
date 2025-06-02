from django.urls import path
from plan.views import InstallmentPlanListCreateAPIView

urlpatterns = [
    path('', InstallmentPlanListCreateAPIView.as_view(), name='installment_plan_list_create_api'),
]
