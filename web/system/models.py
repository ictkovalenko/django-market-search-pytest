from __future__ import unicode_literals, absolute_import

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.html import conditional_escape
from markdown2 import Markdown
from rest_framework import status

from .managers import SystemPropertyQuerySet


class ReviewAbstract(models.Model):
    rating = models.FloatField()
    review = models.CharField(max_length=500, default='', blank=True)
    review_approved = models.BooleanField(default=False)

    created_date = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='+')
    last_modified_date = models.DateTimeField(default=timezone.now)
    last_modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                         null=True, related_name='+')

    class Meta:
        abstract = True

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.review and not self.pk:
            markdown = Markdown()
            # Replace redundant characters from pattern @[text](href:link) to correspond markdown2 format [text](link)
            self.review = markdown.convert(conditional_escape(self.review.replace('@[', '[').replace('(href:', '(')))

        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return '{} {}'.format(self.created_by, self.created_date)

    @property
    def username(self):
        if self.created_by.name:
            return self.created_by.name
        elif self.created_by.first_name and self.created_by.last_name:
            return '{0} {1}.'.format(self.created_by.first_name, self.created_by.last_name[0])
        return self.created_by.email.split('@')[0]


@python_2_unicode_compatible
class SystemProperty(models.Model):
    SYSTEM_PROPERTY_NAME = (
        ('rating_recalculation_size', 'Rating Recalculation Size'),
        ('max_delivery_radius', 'Max Delivery/Proximity Radius'),
        ('auto_email_verification_for_business', 'Auto Email Verification for Business Users'),
    )

    name = models.CharField(max_length=50, choices=SYSTEM_PROPERTY_NAME, unique=True)
    value = models.CharField(max_length=100, blank=False, null=False)

    objects = SystemPropertyQuerySet.as_manager()


class PermanentlyRemoved(models.Model):
    STATUS_CHOICES = (
        (status.HTTP_301_MOVED_PERMANENTLY, status.HTTP_301_MOVED_PERMANENTLY),
        (status.HTTP_410_GONE, status.HTTP_410_GONE)
    )

    url = models.CharField(max_length=255)
    redirect_url = models.CharField(max_length=255, blank=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-pk',)

    def clean(self):
        if self.status == status.HTTP_301_MOVED_PERMANENTLY and not self.redirect_url:
            raise ValidationError({'redirect_url': 'This field is required.'})
