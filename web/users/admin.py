# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.core.urlresolvers import reverse
from django.utils.html import format_html
from impersonate.admin import UserAdminImpersonateMixin
from import_export.admin import ExportActionModelAdmin
from import_export.formats import base_formats
from rangefilter.filter import DateRangeFilter

from web.users.resources import UserResource
from .models import User, UserLocation, UserSetting


class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class MyUserCreationForm(UserCreationForm):
    error_message = UserCreationForm.error_messages.update({
        'duplicate_username': 'This username has already been taken.'
    })

    class Meta(UserCreationForm.Meta):
        model = User

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])


@admin.register(User)
class MyUserAdmin(UserAdminImpersonateMixin, AuthUserAdmin, ExportActionModelAdmin):
    resource_class = UserResource
    formats = (
        base_formats.CSV,
        base_formats.XLS,
    )
    form = MyUserChangeForm
    add_form = MyUserCreationForm
    fieldsets = (
        ('User Profile', {'fields': ('name', 'is_email_verified')}),
        ('', {'fields': ('type', 'timezone', 'proximity', 'gender', 'birth_month', 'birth_day', 'birth_year')}),
    ) + AuthUserAdmin.fieldsets
    list_display = (
        'email', 'first_name', 'last_name', 'type', 'last_login', 'date_joined', 'is_email_verified', 'is_superuser')
    search_fields = ['email', 'first_name', 'last_name']
    list_filter = (
        ('date_joined', DateRangeFilter),
        'type'
    )
    open_new_window = True

    def impersonate_user(self, obj):
        target = ''
        if self.open_new_window:
            target = ' target="_blank"'
        return format_html(
            '<a href="{}"{}>Impersonate</a>',
            reverse('users:impersonate-start', args=[obj.id]),
            target,
        )


@admin.register(UserSetting)
class UserSettingAdmin(admin.ModelAdmin):
    search_fields = ('user__email',)
    list_display = ('user', 'last_modified_date', 'setting_name')


admin.site.register(UserLocation)
