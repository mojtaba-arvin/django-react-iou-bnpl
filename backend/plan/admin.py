from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from plan.models import Plan


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    """Admin interface configuration for Plan model."""

    list_display = ('id', 'name', 'merchant_link', 'total_amount', 'installment_count', 'status')
    list_filter = ('status', 'installment_count')
    search_fields = ('name', 'merchant__email')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('merchant', 'name', 'status')
        }),
        ('Payment Details', {
            'fields': ('total_amount', 'installment_count', 'installment_period')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    @admin.display(description='Merchant')
    def merchant_link(self, obj: Plan) -> str:
        if not obj.merchant:
            return '-'
        url = reverse('admin:account_user_change', args=[obj.merchant.id])
        return format_html('<a href="{}">{}</a>', url, obj.merchant.email)
