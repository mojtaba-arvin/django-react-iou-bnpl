from datetime import datetime, timedelta
from django.test import TestCase
from django.core import mail
from customer.tests.factories import CustomerUserFactory
from installment.models import Installment
from plan.tests.factories import PlanFactory
from installment.tests.factories import InstallmentPlanFactory, InstallmentFactory
from notification.tasks import send_payment_reminders


class PaymentReminderTests(TestCase):
    def setUp(self):
        self.customer = CustomerUserFactory()
        self.plan = PlanFactory()
        self.installment_plan = InstallmentPlanFactory(
            plan=self.plan,
            customer=self.customer
        )

    def test_reminder_for_upcoming_payment(self):
        """Test reminder is sent for installments due in 3 days"""
        due_date = datetime.now().date() + timedelta(days=3)
        InstallmentFactory(
            installment_plan=self.installment_plan,
            due_date=due_date,
            status=Installment.Status.PENDING
        )

        send_payment_reminders()

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('upcoming payment', mail.outbox[0].subject.lower())
        self.assertIn(str(due_date), mail.outbox[0].body)

    def test_no_reminder_for_paid_installments(self):
        """Test no reminder for already paid installments"""
        InstallmentFactory(
            installment_plan=self.installment_plan,
            due_date=datetime.now().date() + timedelta(days=3),
            status=Installment.Status.PAID
        )

        send_payment_reminders()
        self.assertEqual(len(mail.outbox), 0)
