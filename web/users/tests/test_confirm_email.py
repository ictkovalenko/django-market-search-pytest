from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse

from web.search.models import UserSearch
from web.users.tests.factories import UserFactory


class UserSignUpWizardTestCase(TestCase):

    def setUp(self):
        self.user = UserFactory(is_email_verified=False)
        self.url = reverse('users:confirm_email', args=(self.user.pk,))

    def test_confirm_email_without_search_settings(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_email_verified)
        self.assertContains(response, "= '{}'".format(reverse('home')))

    def test_confirm_email_with_search_settings(self):
        UserSearch.objects.create(user=self.user, varieties={}, effects={}, benefits={}, side_effects={})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_email_verified)
        self.assertContains(response, "= '{}'".format(reverse('search:vt_results')))
