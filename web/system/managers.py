from __future__ import unicode_literals, absolute_import

from django.db import models
from django.conf import settings


class SystemPropertyQuerySet(models.QuerySet):

    def max_delivery_radius(self):
        proximity = self.get(name='max_delivery_radius')
        try:
            return int(proximity.value)
        except (ValueError, TypeError):
            return settings.DEFAULT_DELIVERY_RADIUS
