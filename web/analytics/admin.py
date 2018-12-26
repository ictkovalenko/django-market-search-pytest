# -*- coding: utf-8 -*-
from django.contrib import admin
from rangefilter.filter import DateRangeFilter

from web.analytics.models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('event_date', 'event', 'entity_id', 'user')
    search_fields = ('event_date', 'event', 'entity_id', 'user')
    list_filter = (
        ('event_date', DateRangeFilter),
        'event', 'entity_id'
    )
