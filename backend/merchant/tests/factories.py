import factory
from factory.django import DjangoModelFactory
from account.models import User
from merchant.models import MerchantProfile


class MerchantUserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Faker('email')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    user_type = User.UserType.MERCHANT

    # Explicitly save the instance after post-generation hooks to ensure
    # changes (like password hashing) are persisted. This avoids deprecation
    # warnings and aligns with future factory_boy behavior.
    @factory.post_generation
    def save_user(self, create, extracted, **kwargs):
        if create:
            self.save()

class MerchantProfileFactory(DjangoModelFactory):
    class Meta:
        model = MerchantProfile

    user = factory.SubFactory(MerchantUserFactory)
    business_name = factory.Faker('company')
    business_registration_number = factory.Sequence(lambda n: f'REG{n:08d}')
    is_verified = False