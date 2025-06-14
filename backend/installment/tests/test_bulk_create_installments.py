from decimal import Decimal
from datetime import date
from unittest import mock
from typing import List

from django.core.exceptions import ValidationError
from django.test import TestCase
from dateutil.relativedelta import relativedelta
from rest_framework import status

from core.exceptions import BusinessException
from installment.models import Installment
from installment.utils.bulk_create import bulk_create_installments
from installment.utils.signal_control import disable_installment_creation_signal
from plan.tests.factories import PlanFactory
from installment.tests.factories import InstallmentPlanFactory


class BulkCreateInstallmentsTests(TestCase):
    """Tests for the bulk_create_installments utility function."""

    def setUp(self) -> None:
        """
        Set up a valid Plan and its InstallmentPlan without auto‐creation of Installments.

        - Creates a Plan with 3 installments, total_amount=100.00, installment_period=10 days.
        - Creates the corresponding InstallmentPlan with signals disabled.
        - Clears any existing Installment objects from the database.
        """
        self.valid_plan = PlanFactory(
            installment_count=3,
            total_amount=Decimal("100.00"),
            installment_period=10,
        )
        self.today: date = date.today()

        # Disable any post_save signals that might auto‐create Installments.
        with disable_installment_creation_signal():
            self.valid_installment_plan = InstallmentPlanFactory(
                plan=self.valid_plan,
                start_date=self.today,
            )

        Installment.objects.all().delete()

    def test_normal_split_and_rounding(self) -> None:
        """
        Verify that when total_amount=100.00 and installment_count=3:

        - Each of the first two installments is 33.33.
        - The final installment is 33.34 to account for rounding.
        - Due dates are spaced by 10 days: today, today+10, today+20.
        - Sequence numbers are 1, 2, 3.
        """
        Installment.objects.all().delete()

        bulk_create_installments([self.valid_installment_plan])

        installments: List[Installment] = (
            Installment.objects
            .filter(installment_plan=self.valid_installment_plan)
            .order_by("sequence_number")
        )
        self.assertEqual(installments.count(), 3)

        # Verify amounts
        actual_amounts = [inst.amount for inst in installments]
        expected_amounts = [Decimal("33.34"), Decimal("33.33"), Decimal("33.33")]
        self.assertListEqual(actual_amounts, expected_amounts)

        # Verify due dates
        expected_due_dates = [
            self.today + relativedelta(days=10 * (i - 1)) for i in (1, 2, 3)
        ]
        actual_due_dates = [inst.due_date for inst in installments]
        self.assertListEqual(actual_due_dates, expected_due_dates)

        # Verify sequence numbers
        actual_sequences = [inst.sequence_number for inst in installments]
        self.assertListEqual(actual_sequences, [1, 2, 3])

    def test_skip_invalid_plans_do_not_create_installments(self) -> None:
        """
        If installment_count <= 0 or total_amount <= 0, bulk_create_installments
        must skip those plans without raising an exception, resulting in zero
        Installment objects created.
        """
        Installment.objects.all().delete()

        # Create four “invalid” Plan instances by overriding in memory.
        # 1) installment_count = 0
        plan_invalid_zero_count = PlanFactory(
            installment_count=3,
            total_amount=Decimal("50.00"),
            installment_period=5,
        )
        plan_invalid_zero_count.installment_count = 0
        with disable_installment_creation_signal():
            ip_invalid_zero_count = InstallmentPlanFactory(
                plan=plan_invalid_zero_count,
                start_date=self.today,
            )

        # 2) installment_count < 0
        plan_invalid_negative_count = PlanFactory(
            installment_count=3,
            total_amount=Decimal("50.00"),
            installment_period=5,
        )
        plan_invalid_negative_count.installment_count = -2
        with disable_installment_creation_signal():
            ip_invalid_negative_count = InstallmentPlanFactory(
                plan=plan_invalid_negative_count,
                start_date=self.today,
            )

        # 3) total_amount = 0
        plan_invalid_zero_amount = PlanFactory(
            installment_count=3,
            total_amount=Decimal("50.00"),
            installment_period=5,
        )
        plan_invalid_zero_amount.total_amount = Decimal("0.00")
        with disable_installment_creation_signal():
            ip_invalid_zero_amount = InstallmentPlanFactory(
                plan=plan_invalid_zero_amount,
                start_date=self.today,
            )

        # 4) total_amount < 0
        plan_invalid_negative_amount = PlanFactory(
            installment_count=3,
            total_amount=Decimal("50.00"),
            installment_period=5,
        )
        plan_invalid_negative_amount.total_amount = Decimal("-10.00")
        with disable_installment_creation_signal():
            ip_invalid_negative_amount = InstallmentPlanFactory(
                plan=plan_invalid_negative_amount,
                start_date=self.today,
            )

        bulk_create_installments([
            ip_invalid_zero_count,
            ip_invalid_negative_count,
            ip_invalid_zero_amount,
            ip_invalid_negative_amount,
        ])

        # After running, there should be no Installment rows.
        self.assertEqual(Installment.objects.count(), 0)

    def test_business_exception_on_rounding_to_zero_or_negative(self) -> None:
        """
        Force a situation where rounding causes a zero or negative installment amount.

        Example:
        total_amount=1.00, installment_count=101 → base = round(1/101, 2) = 0.01,
        0.01 * 100 = 1.00, final = 1.00 - 1.00 = 0.00, which is invalid.
        """
        Installment.objects.all().delete()

        # Create a valid Plan, then override for rounding error test
        plan_rounding_error = PlanFactory(
            installment_count=101,
            total_amount=Decimal("1.00"),
            installment_period=1,
        )
        with disable_installment_creation_signal():
            ip_rounding_error = InstallmentPlanFactory(
                plan=plan_rounding_error,
                start_date=self.today,
            )

        with self.assertRaises(BusinessException) as exc_info:
            bulk_create_installments([ip_rounding_error])

        self.assertEqual(
            exc_info.exception.status_code,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
        self.assertEqual(
            Installment.objects.filter(installment_plan=ip_rounding_error).count(),
            0,
        )

    def test_business_exception_on_full_clean_failure(self) -> None:
        """
        If any Installment.full_clean() raises ValidationError, bulk_create_installments
        should catch it and re‐raise BusinessException.

        We patch Installment.full_clean to always raise a ValidationError.
        """
        Installment.objects.all().delete()

        # Create a valid Plan for this test
        plan_for_validation = PlanFactory(
            installment_count=2,
            total_amount=Decimal("20.00"),
            installment_period=7,
        )
        with disable_installment_creation_signal():
            ip_for_validation = InstallmentPlanFactory(
                plan=plan_for_validation,
                start_date=self.today,
            )

        # Patch Installment.full_clean to always raise
        with mock.patch.object(
            Installment, "full_clean", side_effect=ValidationError("Forced")
        ):
            with self.assertRaises(BusinessException) as exc_info:
                bulk_create_installments([ip_for_validation])

            self.assertEqual(
                exc_info.exception.status_code,
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
