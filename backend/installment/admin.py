from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from installment.models import InstallmentPlan, Installment


class InstallmentInline(admin.TabularInline):
    """Inline admin interface for Installment within InstallmentPlan."""
    model = Installment
    extra = 0
    readonly_fields = ('due_date', 'sequence_number', 'created_at')
    fields = ('amount', 'due_date', 'status', 'paid_at', 'sequence_number')


@admin.register(InstallmentPlan)
class InstallmentPlanAdmin(admin.ModelAdmin):
    """Admin interface for InstallmentPlan model."""
    list_display = ('id', 'plan_link', 'customer_link', 'status', 'start_date')
    list_filter = ('status', 'plan__merchant')
    search_fields = ('customer__email', 'plan__name')
    inlines = [InstallmentInline]
    readonly_fields = ('created_at', 'updated_at')

    @admin.display(description='Plan')
    def plan_link(self, obj: InstallmentPlan) -> str:
        """Generate a hyperlink to the related Plan object in admin."""
        if not obj.plan:
            return '-'
        url = reverse('admin:plan_plan_change', args=[obj.plan.id])
        return format_html('<a href="{}">{}</a>', url, obj.plan.name)

    @admin.display(description='Customer')
    def customer_link(self, obj: InstallmentPlan) -> str:
        """Generate a hyperlink to the related Customer object in admin."""
        if not obj.customer:
            return '-'
        url = reverse('admin:account_user_change', args=[obj.customer.id])
        return format_html('<a href="{}">{}</a>', url, obj.customer.email)


@admin.register(Installment)
class InstallmentAdmin(admin.ModelAdmin):
    """Admin interface for Installment model."""
    list_display = ('id', 'installment_plan', 'amount', 'due_date', 'status')
    list_filter = ('status', 'installment_plan__plan__merchant')
    search_fields = ('installment_plan__customer__email',)
    readonly_fields = ('created_at', 'updated_at')
