import random

import factory.faker
from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth.hashers import make_password

from web.users.models import GENDER

TEST_USER_PASSWORD = 'P4ssw0rd'


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = settings.AUTH_USER_MODEL

    name = factory.Faker('name')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Sequence(lambda n: 'user_{0}@email.com'.format(n))
    username = factory.LazyAttribute(lambda x: x.email)
    password = make_password(TEST_USER_PASSWORD)
    is_age_verified = True
    is_email_verified = True
    type = 'consumer'
    gender = factory.LazyAttribute(lambda x: random.choice(GENDER)[0])

    @factory.post_generation
    def emailaddress(self, create, extracted, **kwargs):
        if not create or extracted:
            return
        EmailAddress.objects.create(user=self, email=self.email, verified=True, primary=True)


class BusinessUserFactory(UserFactory):
    class Meta:
        model = settings.AUTH_USER_MODEL

    type = 'business'
