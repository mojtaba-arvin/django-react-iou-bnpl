from typing import List, Optional

from django.contrib import admin
from django.contrib.admin.options import InlineModelAdmin
from django.http import HttpRequest
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from customer.admin import CustomerProfileInline
from merchant.admin import MerchantProfileInline

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(DjangoUserAdmin):
    """Custom admin interface for the User model."""

    list_display = ('email', 'user_type', 'is_active', 'is_staff')
    list_filter = ('user_type', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            'Permissions',
            {
                'fields': (
                    'user_type',
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                )
            },
        ),
    )
    list_editable = ('is_active',)
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'email',
                    'password1',
                    'password2',
                    'user_type',
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                ),
            },
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)

    def get_inline_instances(
        self, request: HttpRequest, obj: Optional[User] = None
    ) -> List[InlineModelAdmin]:
        """
        Return the appropriate inline instance(s) based on the user's type.

        Args:
            request (HttpRequest): The current admin request instance.
            obj (Optional[User]): The user object being edited.

        Returns:
            List[InlineModelAdmin]: A list of instantiated inline admin classes to display in the admin.
        """
        if not obj:
            return []

        if obj.user_type == User.UserType.CUSTOMER:
            return [CustomerProfileInline(self.model, self.admin_site)]
        if obj.user_type == User.UserType.MERCHANT:
            return [MerchantProfileInline(self.model, self.admin_site)]
        return []

    add_fieldsets = DjangoUserAdmin.add_fieldsets
