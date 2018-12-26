from django.db import models


class EventQuerySet(models.QuerySet):

    def events(self, from_date, to_date, entity_id, event_type):
        query = self.filter(entity_id=entity_id)
        if isinstance(event_type, (list, tuple)):
            query = query.filter(event__in=event_type)
        else:
            query = query.filter(event=event_type)

        if from_date:
            query = query.filter(event_date__gte=from_date)

        if to_date:
            query = query.filter(event_date__lte=to_date)
        return query

    def group_by_date(self):
        return self \
            .extra(select={'day': 'to_char( event_date,  \'YYYY-MM-DD\' )'}) \
            .values('day') \
            .annotate(count=models.Count('event_date')) \
            .order_by('day')
