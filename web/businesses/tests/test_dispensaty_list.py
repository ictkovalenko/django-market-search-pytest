from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse

from web.analytics.models import Event
from web.businesses.tests.factories import BusinessLocationFactory
from web.users.tests.factories import BusinessUserFactory


class DispensariesListTestCase(TestCase):
    def setUp(self):
        self.user = BusinessUserFactory()
        self.locations = BusinessLocationFactory.create_batch(5, dispensary=True)
        self.url = reverse('businesses:dispensaries_list')

    def test_get_dispensaries_list_by_anonymous_user(self):
        """
        Anonymous user goes to dispensaries list page
        and 3 featured_disp event are created
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Event.objects.count(), 3)
        self.assertEqual(Event.objects.filter(event=Event.FEATURED_DISP).count(), 3)

    def test_get_dispensaries_list_by_user(self):
        """
        Anonymous user goes to dispensaries list page
        and 3 featured_disp event are created
        """
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Event.objects.count(), 3)
        self.assertEqual(Event.objects.filter(event=Event.FEATURED_DISP).count(), 3)
