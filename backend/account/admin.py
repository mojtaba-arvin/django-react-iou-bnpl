from typing import List, Optional, Type

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.admin import StackedInline

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

    def get_inlines(
        self, request: admin.options.Request, obj: Optional[User] = None
    ) -> List[Type[StackedInline]]:
        """
        Return the appropriate inline(s) based on the user's type.

        Args:
            request (Request): The current admin request instance.
            obj (Optional[User]): The user object being edited.

        Returns:
            List[Type[StackedInline]]: A list of inlines to display in the admin.
        """
        if not obj:
            return []

        if obj.user_type == User.UserType.CUSTOMER:
            return [CustomerProfileInline]
        if obj.user_type == User.UserType.MERCHANT:
            return [MerchantProfileInline]
        return []

    add_fieldsets = DjangoUserAdmin.add_fieldsets
