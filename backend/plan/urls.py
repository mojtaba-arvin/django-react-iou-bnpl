from django.urls import path
from plan.views import PlanListCreateAPIView

urlpatterns = [
    path('', PlanListCreateAPIView.as_view(), name='plan_list_create_api'),
]
