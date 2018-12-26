from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible

from web.analytics.querysets import EventQuerySet
from web.users.models import User
from web.users.models import User


@python_2_unicode_compatible
class Event(models.Model):
    DISP_LOOKUP = 'DISP_LOOKUP'
    DISP_CALL = 'DISP_CALL'
    VIEW_DISP_AVAIL_AT = 'VIEW_DISP_AVAIL_AT'
    VIEW_DISP = 'VIEW_DISP'
    DISP_GETDIR = 'DISP_GETDIR'
    FEATURED_DISP = 'FEATURED_DISP'
    FEATURED_CLICK = 'FEATURED_CLICK'

    event = models.CharField(max_length=24, blank=False, null=False, db_index=True)
    entity_id = models.IntegerField(blank=False, null=False)
    user = models.ForeignKey(User, blank=True, null=True)
    event_date = models.DateTimeField(default=timezone.now, db_index=True)
    properties = JSONField()

    objects = EventQuerySet.as_manager()

    class Meta:
        verbose_name = 'Event'
        verbose_name_plural = 'Events'

    def __str__(self):
        return '{} {}'.format(self.entity_id, self.event)
