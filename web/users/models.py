# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import json
import urllib.parse
from uuid import uuid4

import pytz
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import AnonymousUser
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from web.users import validators
from web.system.models import SystemProperty


USER_TYPE = [
    ('admin', 'Admin'),
    ('business', 'Business'),
    ('consumer', 'Consumer')
]

GENDER = [
    ('male', 'Male'),
    ('female', 'Female'),
]


def upload_image_to(instance, filename):
    return 'users/{0}/images/{1}___{2}'.format(instance.pk, uuid4(), filename)


@python_2_unicode_compatible
class User(AbstractUser):
    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = models.CharField(_('Name of User'), blank=True, max_length=25)

    is_age_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    display_search_history = models.BooleanField(default=True, editable=False)
    type = models.CharField(max_length=10, choices=USER_TYPE, default='consumer')

    birth_month = models.CharField(_('Birth Month'), blank=True, null=True, max_length=20)
    birth_day = models.IntegerField(_('Birth Day'), blank=True, null=True)
    birth_year = models.IntegerField(_('Birth Year'), blank=True, null=True)

    gender = models.CharField(_('Gender'), choices=GENDER, blank=True, null=True, max_length=10)
    proximity = models.FloatField(_('Proximity'), null=True)
    timezone = models.CharField(_('Timezone'), null=True, max_length=100,
                                choices=zip(pytz.common_timezones, pytz.common_timezones))

    image = models.ImageField(max_length=255, upload_to=upload_image_to, blank=True,
                              help_text='Maximum file size allowed is 5Mb', validators=[validators.validate_image])

    def clean(self):
        validators.validate_email(self.email)
        validators.validate_name(self.name, self.pk)
        if not self.is_age_verified:
            return ValidationError('Age verification is required')

    def save(self, *args, **kwargs):
        self.clean()
        super(User, self).save(*args, **kwargs)

    def __str__(self):
        return self.email

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'user_id': self.id})

    def get_location(self):
        if UserLocation.objects.filter(user__id=self.pk).exists():
            return UserLocation.objects.get(user__id=self.pk)

        return None

    def get_location_json(self):
        if UserLocation.objects.filter(user__id=self.pk).exists():
            location = UserLocation.objects.get(user__id=self.pk)
            return {
                "street1": location.street1 if location.street1 else "",
                "city": location.city if location.city else "",
                "state": location.state if location.state else "",
                "zipcode": location.zipcode if location.zipcode else "",
                "location_raw": location.location_raw if location.location_raw else {}
            }
        return {}


@python_2_unicode_compatible
class CustomAnonymousUser(AnonymousUser):
    def __init__(self, request):
        super().__init__()
        self.request = request

    @property
    def proximity(self):
        return SystemProperty.objects.max_delivery_radius()

    def get_location(self):
        raw_location = self.request.COOKIES.get('user_geo_location')
        if raw_location is None:
            return None

        deserialized = json.loads(urllib.parse.unquote(raw_location))
        user_location = UserLocation()
        user_location.street1 = deserialized['street1']
        user_location.city = deserialized['city']
        user_location.state = deserialized['state']
        user_location.zipcode = deserialized['zipcode']
        user_location.lat = deserialized['lat']
        user_location.lng = deserialized['lng']

        return user_location


@python_2_unicode_compatible
class PwResetLink(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    token = models.CharField(max_length=100)
    last_modified_date = models.DateTimeField(auto_now=True)


@python_2_unicode_compatible
class UserSetting(models.Model):
    class Meta:
        unique_together = (("user", "setting_name"),)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    setting_name = models.CharField(max_length=100)
    setting_value = JSONField(max_length=4096, default={})
    last_modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0} - {1}'.format(self.user, self.last_modified_date)

    @staticmethod
    def create_for_user(user, user_settings):
        for s in user_settings:
            UserSetting.objects.get_or_create(
                user=user,
                setting_name=s.get('setting_name'),
                setting_value=s.get('setting_value'),
            )


@python_2_unicode_compatible
class UserLocation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='geo_location')

    street1 = models.CharField(_('Street'), blank=True, null=True, max_length=100)
    city = models.CharField(_('City'), blank=True, null=True, max_length=100)
    state = models.CharField(_('State'), blank=True, null=True, max_length=50)
    zipcode = models.CharField(_('Zip Code'), blank=True, null=True, max_length=10)

    lat = models.FloatField(_('Latitude'), blank=True, null=True, max_length=50)
    lng = models.FloatField(_('Longitude'), blank=True, null=True, max_length=50)
    location_raw = JSONField(_('Location Raw JSON'), default={}, max_length=20000)
    last_modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} {}, {} {}'.format(self.street1, self.city, self.state, self.zipcode)
