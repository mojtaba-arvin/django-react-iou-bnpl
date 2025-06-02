from datetime import date
from typing import Dict, List, Tuple

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request

from core.validators import BaseValidator
from customer.models import CustomerProfile

User = get_user_model()


class StartDateValidator(BaseValidator):
    """Validator for installment plan start date."""

    def validate(self, data: Dict, request: Request) -> Dict:
        """Validate start date is not in the past.

        Args:
            data: Input data containing optional start_date
            request: DRF request object

        Returns:
            Validated data

        Raises:
            ValidationError: If start_date is in the past
        """
        start_date = data.get('start_date', date.today())
        if start_date < date.today():
            raise ValidationError({
                "start_date": _("Start date cannot be in the past.")
            })
        return data


class TotalAmountValidator(BaseValidator):
    """Validator for installment plan total amount."""

    def validate(self, data: Dict, request: Request) -> Dict:
        """Validate total amount is a positive number.

        Args:
            data: Input data containing optional start_date
            request: DRF request object

        Returns:
            Validated data

        Raises:
            ValidationError: If total_amount is not a positive number
        """
        total_amount = data.get('total_amount')
        if total_amount is None or total_amount <= 0:
            raise ValidationError({
                'total_amount': _('Total amount must be a positive number.')
            })
        return data


class InstallmentCountValidator(BaseValidator):
    """Validator for installment plan installments count."""

    def validate(self, data: Dict, request: Request) -> Dict:
        """Validate installments count is a positive number.

        Args:
            data: Input data containing optional start_date
            request: DRF request object

        Returns:
            Validated data

        Raises:
            ValidationError: If installment_count is not a positive number
        """
        installment_count = data.get('installment_count')
        if installment_count is None or installment_count <= 0:
            raise ValidationError({
                'installment_count': _('Installment count must be a positive integer.')
            })
        return data


class CustomerValidator(BaseValidator):
    """Validator for mutual exclusivity of customer identifiers."""

    def validate(self, data: Dict, request: Request) -> Dict:
        """Validate only one customer identifier is provided.

        Args:
            data: Input data containing customer_ids and/or customer_email
            request: DRF request object

        Returns:
            Validated data

        Raises:
            ValidationError: If both customer_ids and customer_email are provided
        """
        customer_ids = data.get("customer_ids", [])
        customer_email = data.get("customer_email")

        if customer_ids and customer_email:
            raise ValidationError(
                _("customer_ids and customer_email cannot be used together.")
            )
        return data


class CustomerIdsValidator(BaseValidator):
    """Validator for customer IDs list."""

    def validate(self, data: Dict, request: Request) -> List[User]:
        """Validate and fetch customers by IDs.

        Args:
            data: Input data containing customer_ids list
            request: DRF request object

        Returns:
            List of validated User objects

        Raises:
            ValidationError: If any IDs are invalid or customers ineligible
        """
        customer_ids = data.get("customer_ids", [])
        if not customer_ids:
            return []

        eligible_customers_qs = User.objects.filter(
            id__in=customer_ids,
            user_type=User.UserType.CUSTOMER,
            customer_profile__score_status=CustomerProfile.ScoreStatus.APPROVED,
            customer_profile__is_active=True,
        ).select_related("customer_profile")

        eligible_ids = {user.id for user in eligible_customers_qs}
        ineligible_ids = set(customer_ids) - eligible_ids

        if ineligible_ids:
            raise ValidationError({
                "customer_ids": _(
                    f"The following customer IDs are not eligible: {sorted(ineligible_ids)}"
                )
            })

        return list(eligible_customers_qs)


class CustomerEmailValidator(BaseValidator):
    """Validator for customer email."""

    def validate(self, data: Dict, request: Request) -> List[User]:
        """Validate and fetch customer by email.

        Args:
            data: Input data containing customer_email
            request: DRF request object

        Returns:
            List containing single validated User object

        Raises:
            ValidationError: If email is invalid or customer ineligible
        """
        customer_email = data.get("customer_email")
        if not customer_email:
            return []

        try:
            customer = User.objects.get(
                email=customer_email,
                user_type=User.UserType.CUSTOMER,
                customer_profile__score_status=CustomerProfile.ScoreStatus.APPROVED,
                customer_profile__is_active=True,
            )
            return [customer]
        except User.DoesNotExist:
            raise ValidationError({
                "customer_email": _("No eligible customer found with this email.")
            })


class PlanValidator:
    """Orchestrates validation for plan creation."""

    def __init__(self) -> None:
        """Initialize with required validators."""
        self.validators = [
            StartDateValidator(),
            TotalAmountValidator(),
            InstallmentCountValidator(),
            # CustomerValidator(),  # TODO(mojtaba - 2025-06-02): check if needed to support customer_ids and customer_email together
        ]

        # to get customer instance(s) after run validations
        self.customer_validators = [
            # CustomerIdsValidator(),  # TODO(mojtaba - 2025-06-02): check if needed to support customer_ids
            CustomerEmailValidator(),
        ]

    def validate(self, data: Dict, request: Request) -> Tuple[Dict, List[User]]:
        """Run complete validation pipeline.

        Args:
            data: Input data for plan creation
            request: DRF request object

        Returns:
            Tuple of (validated data, list of customer objects)

        Raises:
            ValidationError: If any validation fails
        """
        # Run basic validations
        for validator in self.validators:
            data = validator.validate(data, request)

        # Run customer validations and get customers
        customers = []
        for validator in self.customer_validators:
            try:
                customers.extend(validator.validate(data, request))
            except ValidationError as e:
                raise e

        return data, customers
