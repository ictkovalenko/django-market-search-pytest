import random

import factory.faker

from web.search.models import Vt


class VtFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Vt

    name = factory.Faker('name')
    variety = factory.LazyAttribute(lambda x: random.choice(Vt.VARIETY_CHOICES)[0])
    category = factory.LazyAttribute(lambda x: random.choice(Vt.CATEGORY_CHOICES)[0])
