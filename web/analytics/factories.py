import random

import factory
from django.utils import timezone

from web.analytics.models import Event
from web.businesses.tests.factories import BusinessFactory
from web.users.tests.factories import BusinessUserFactory


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event

    event = factory.LazyAttribute(lambda x: random.choice([
        Event.DISP_LOOKUP, Event.DISP_CALL, Event.VIEW_DISP_AVAIL_AT, Event.VIEW_DISP, Event.DISP_GETDIR,
        Event.FEATURED_DISP, Event.FEATURED_CLICK]))
    entity_id = factory.LazyAttribute(lambda x: BusinessFactory().pk)
    user = factory.SubFactory(BusinessUserFactory)
    event_date = factory.LazyAttribute(lambda x: timezone.now() - timezone.timedelta(days=random.randint(0, 365)))
    properties = {}
