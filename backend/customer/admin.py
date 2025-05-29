from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import CustomerProfile


class CustomerProfileInline(admin.StackedInline):
    """Inline for CustomerProfile in the User admin."""

    model = CustomerProfile
    can_delete = False
    fields = ('score_status', 'credit_score', 'is_active')
    verbose_name_plural = _('Customer Profile')


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    """Admin for managing CustomerProfile separately."""

    list_display = ('user_email', 'credit_score', 'score_status', 'is_active')
    list_filter = ('score_status', 'is_active')
    search_fields = ('user__email',)
    readonly_fields = ('created_at', 'updated_at')

    @admin.display(description=_('User Email'))
    def user_email(self, obj: CustomerProfile) -> str:
        """Display the email of the user associated with the customer profile."""
        return obj.user.email
