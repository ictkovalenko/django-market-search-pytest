# -*- coding: utf-8 -*-
from django.contrib import admin

from web.system.models import SystemProperty, PermanentlyRemoved


@admin.register(SystemProperty)
class SystemPropertyAdmin(admin.ModelAdmin):
    list_display = ['name', 'value']
    search_fields = ['name', 'value']
    list_filter = ['name', 'value']
    ordering = ['name']


@admin.register(PermanentlyRemoved)
class PermanentlyRemovedAdmin(admin.ModelAdmin):
    list_display = ('url', 'status', 'redirect_url')
