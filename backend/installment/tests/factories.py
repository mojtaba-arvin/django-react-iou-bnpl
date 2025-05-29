import factory
from factory.django import DjangoModelFactory
from account.models import User
from installment.models import InstallmentPlan, Installment
from datetime import date, timedelta


class CustomerFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f'customer{n}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    user_type = User.UserType.CUSTOMER


class InstallmentPlanFactory(DjangoModelFactory):
    class Meta:
        model = InstallmentPlan

    plan = factory.SubFactory('plan.tests.factories.PlanFactory')
    customer = factory.SubFactory(CustomerFactory)
    start_date = factory.LazyAttribute(lambda _: date.today())  # Use LazyAttribute for flexibility


class InstallmentFactory(DjangoModelFactory):
    class Meta:
        model = Installment

    installment_plan = factory.SubFactory(InstallmentPlanFactory)
    amount = 250.00
    due_date = factory.LazyAttribute(
        lambda o: o.installment_plan.start_date + timedelta(days=30 * o.sequence_number)
    )
    sequence_number = factory.Sequence(lambda n: n + 1)  # Use Sequence for guaranteed uniqueness
    status = Installment.Status.PENDING
