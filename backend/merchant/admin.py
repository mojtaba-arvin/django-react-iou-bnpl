from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import MerchantProfile


class MerchantProfileInline(admin.StackedInline):
    """Inline admin configuration for MerchantProfile in the User admin page."""

    model = MerchantProfile
    can_delete = False
    fields = ('business_name', 'business_registration_number', 'is_verified')
    verbose_name_plural = _('Merchant Profile')


@admin.register(MerchantProfile)
class MerchantProfileAdmin(admin.ModelAdmin):
    """Admin interface for managing MerchantProfile directly."""

    list_display = ('user_email', 'business_name', 'is_verified')
    list_filter = ('is_verified',)
    search_fields = ('user__email',)

    @admin.display(description=_('User Email'))
    def user_email(self, obj: MerchantProfile) -> str:
        """Return the email of the associated user
        """
        return obj.user.email
