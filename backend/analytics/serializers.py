from rest_framework import serializers


class MerchantDashboardMetricsSerializer(serializers.Serializer):
    total_revenue = serializers.DecimalField(
        max_digits=12, decimal_places=2, coerce_to_string=False
    )
    success_rate = serializers.FloatField()
    overdue_count = serializers.IntegerField()
    active_plans = serializers.IntegerField()
