from typing import Any, Optional

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import AbstractTimestampedModel


class UserManager(BaseUserManager):
    """Manager for custom User model."""

    def create_user(
        self,
        email: str,
        password: Optional[str] = None,
        user_type: Optional[str] = None,
        **extra_fields: Any
    ) -> 'User':
        """
        Create and return a regular user with the given email and password.

        Args:
            email (str): The user's email address.
            password (Optional[str]): The user's password.
            user_type (Optional[str]): The type of user (customer/merchant).
            **extra_fields (Any): Additional fields for the user.

        Returns:
            User: The created user instance.

        Raises:
            ValueError: If the email is not provided.
        """
        if not email:
            raise ValueError('Users must have an email address')

        # Ensure user_type is set or defaults to CUSTOMER
        user_type = user_type or self.model.UserType.CUSTOMER

        user = self.model(
            email=self.normalize_email(email),
            user_type=user_type,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        email: str,
        password: str,
        **extra_fields: Any
    ) -> 'User':
        """
        Create and return a superuser with the given email and password.

        Args:
            email (str): The superuser's email address.
            password (str): The superuser's password.
            **extra_fields (Any): Additional fields for the superuser.

        Returns:
            User: The created superuser instance.

        Raises:
            ValueError: If required superuser flags are not set.
        """
        extra_fields.setdefault('user_type', self.model.UserType.MERCHANT)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser must have is_staff=True.')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractTimestampedModel, AbstractBaseUser, PermissionsMixin):
    """Custom user model with email authentication and user type roles."""

    class UserType(models.TextChoices):
        CUSTOMER = 'customer', _('Customer')
        MERCHANT = 'merchant', _('Merchant')

    email = models.EmailField(_('email address'), unique=True)
    user_type = models.CharField(
        _('user type'),
        max_length=10,
        choices=UserType.choices,
        default=UserType.CUSTOMER,
        db_index=True
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_('Can this user login to system?'),
    )
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def __str__(self) -> str:
        """
        Return a string representation of the user.

        Returns:
            str: The user's email and type.
        """
        return f"{self.email} ({self.user_type})"

    def has_perm(self, perm: str, obj: Optional[Any] = None) -> bool:
        """
        Check if user has a specific permission.

        Args:
            perm (str): The permission to check.
            obj (Optional[Any]): An optional object for permission check.

        Returns:
            bool: True if user has the permission.
        """
        return self.is_staff

    def has_module_perms(self, app_label: str) -> bool:
        """
        Check if user has permissions to view the app `app_label`.

        Args:
            app_label (str): The app label.

        Returns:
            bool: True if user has module-level permissions.
        """
        return self.is_staff

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-created_at']
