from django.test import TestCase
from datetime import date, timedelta

from installment.models import Installment
from plan.tests.factories import PlanFactory
from installment.tests.factories import InstallmentPlanFactory, InstallmentFactory
from installment.services.status import mark_overdue_installments

class OverdueDetectionTest(TestCase):
    """Test suite for detecting overdue installments.

    Verifies that installments with due dates in the past are correctly
    marked as late when the overdue detection function is called.
    """

    def setUp(self):
        self.plan = PlanFactory()
        self.installment_plan = InstallmentPlanFactory(plan=self.plan)

    def test_overdue_detection(self):
        """Test that overdue installments are marked as late."""
        # Create an installment with a due date in the past
        installment = InstallmentFactory(
            installment_plan=self.installment_plan,
            due_date=date.today() - timedelta(days=1),
            status=Installment.Status.PENDING
        )

        # Call the service to mark overdue installments
        mark_overdue_installments()

        # Refresh installment status from the database and check if it's marked as late
        installment.refresh_from_db()
        self.assertEqual(installment.status, Installment.Status.LATE)
