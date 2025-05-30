import factory
from factory.django import DjangoModelFactory
from account.models import User
from customer.constants import CREDIT_SCORE_MIN, CREDIT_SCORE_MAX
from customer.models import CustomerProfile


class CustomerUserFactory(DjangoModelFactory):
    """
    Factory for creating `User` instances for customers.

    This factory generates a user with an email, password (set using `set_password` method),
    and a `user_type` of `CUSTOMER`.
    """

    class Meta:
        model = User

    email = factory.Faker('email')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    user_type = User.UserType.CUSTOMER

    # Explicitly save the instance after post-generation hooks to ensure
    # changes (like password hashing) are persisted. This avoids deprecation
    # warnings and aligns with future factory_boy behavior.
    @factory.post_generation
    def save_user(self, create, extracted, **kwargs):
        if create:
            self.save()


class CustomerProfileFactory(DjangoModelFactory):
    """
    Factory for creating `CustomerProfile` instances.

    This factory generates a profile for a customer with a `credit_score` within the range
    defined by `CREDIT_SCORE_MIN` and `CREDIT_SCORE_MAX`, and sets the `is_active` flag to True.
    """

    class Meta:
        model = CustomerProfile

    user = factory.SubFactory(CustomerUserFactory)
    credit_score = factory.Faker('random_int', min=CREDIT_SCORE_MIN, max=CREDIT_SCORE_MAX)
    is_active = True
