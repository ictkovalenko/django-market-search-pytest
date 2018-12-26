import random

from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse

from web.analytics.factories import EventFactory
from web.analytics.models import Event
from web.businesses.tests.factories import BusinessFactory
from web.users.tests.factories import BusinessUserFactory


class BusinessAnalyticsTestCase(TestCase):
    def setUp(self):
        self.user = BusinessUserFactory()
        self.business = BusinessFactory(created_by=self.user)
        self.url = reverse('businesses:analytics', args=(self.business.pk,))
        self.today = timezone.now()
        self.lookup_event_this_week = EventFactory(
            entity_id=self.business.pk, event=Event.DISP_LOOKUP,
            event_date=self.today - timezone.timedelta(days=random.randint(1, 6)))
        self.lookup_event_this_month = EventFactory(
            entity_id=self.business.pk, event=Event.DISP_LOOKUP,
            event_date=self.today - timezone.timedelta(days=random.randint(8, 20)))

        self.search_event_this_week = EventFactory(
            entity_id=self.business.pk, event=Event.VIEW_DISP_AVAIL_AT,
            event_date=self.lookup_event_this_week.event_date)
        self.search_event_this_month = EventFactory(
            entity_id=self.business.pk, event=Event.VIEW_DISP_AVAIL_AT,
            event_date=self.lookup_event_this_month.event_date)

        session = self.client.session
        session['business'] = {'id': self.business.id}
        session.save()

    def test_analytics_default(self):
        """
        Analytics by default shows for the previous 7 days
        """
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, str([{'day': self.lookup_event_this_week.event_date.strftime('%Y-%m-%d'), 'count': 1}]))
        self.assertContains(response, str([{'day': self.search_event_this_week.event_date.strftime('%Y-%m-%d'), 'count': 1}]))

    def test_filter_by_previous_month(self):
        """
        Display analytics for specific date range
        """
        self.client.force_login(self.user)
        response = self.client.get('{}?from_date={}&to_date={}'.format(
            self.url, (self.today - timezone.timedelta(days=30)).strftime('%Y-%m-%d'), self.today.strftime('%Y-%m-%d')))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, str([
            {'day': self.lookup_event_this_month.event_date.strftime('%Y-%m-%d'), 'count': 1},
            {'day': self.lookup_event_this_week.event_date.strftime('%Y-%m-%d'), 'count': 1}]))
        self.assertContains(response, str([
            {'day': self.search_event_this_month.event_date.strftime('%Y-%m-%d'), 'count': 1},
            {'day': self.search_event_this_week.event_date.strftime('%Y-%m-%d'), 'count': 1}]))

    def test_filter_by_from_date(self):
        """
        Display analytics by from date
        """
        self.client.force_login(self.user)
        response = self.client.get('{}?from_date={}'.format(
            self.url, (self.today - timezone.timedelta(days=30)).strftime('%Y-%m-%d')))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, str([
            {'day': self.lookup_event_this_month.event_date.strftime('%Y-%m-%d'), 'count': 1},
            {'day': self.lookup_event_this_week.event_date.strftime('%Y-%m-%d'), 'count': 1}]))
        self.assertContains(response, str([
            {'day': self.search_event_this_month.event_date.strftime('%Y-%m-%d'), 'count': 1},
            {'day': self.search_event_this_week.event_date.strftime('%Y-%m-%d'), 'count': 1}]))

    def test_filter_by_to_date(self):
        """
        Display analytics by to date
        """
        self.client.force_login(self.user)
        response = self.client.get('{}?to_date={}'.format(
            self.url, self.lookup_event_this_month.event_date.strftime('%Y-%m-%d')))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, str([
            {'day': self.lookup_event_this_month.event_date.strftime('%Y-%m-%d'), 'count': 1}]))
        self.assertContains(response, str([
            {'day': self.search_event_this_month.event_date.strftime('%Y-%m-%d'), 'count': 1}]))

    def test_user_not_authorized(self):
        """
        Anonymous user does not have access to the analytics page
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('home'))

    def test_wrong_date(self):
        """
        User enter wrong date and redirected to the same page
        """
        self.client.force_login(self.user)
        response = self.client.get('{}?from={}&to={}'.format(
            self.url, self.today.strftime('%Y-%m-%d'), self.today.strftime('%Y-%Y-%d')))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, str([{'day': self.lookup_event_this_week.event_date.strftime('%Y-%m-%d'), 'count': 1}]))
