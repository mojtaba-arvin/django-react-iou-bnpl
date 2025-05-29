from rest_framework import serializers
from installment.models import Installment, InstallmentPlan


class InstallmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Installment
        fields = [
            "id",
            "amount",
            "due_date",
            "status",
            "sequence_number",
            "paid_at",
        ]


class InstallmentPlanSerializer(serializers.ModelSerializer):

    class Meta:
        model = InstallmentPlan
        fields = [
            # "id",
            "start_date",
            "status",
        ]
