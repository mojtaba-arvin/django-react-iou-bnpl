
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class EligibleCustomerSerializer(serializers.ModelSerializer):
    credit_score = serializers.IntegerField(source="customer_profile.credit_score")
    score_status = serializers.CharField(source="customer_profile.score_status")
    is_active = serializers.BooleanField(source="customer_profile.is_active")

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "credit_score",
            "score_status",
            "is_active",
        ]
