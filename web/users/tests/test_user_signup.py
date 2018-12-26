from django.contrib.auth import get_user_model
from django.utils import lorem_ipsum
from mock import patch
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from web.search.models import UserSearch
from web.users.emails import EmailService
from web.users.models import UserLocation
from web.users.tests.factories import UserFactory


class UserSignUpWizardTestCase(APITestCase):

    def setUp(self):
        self.url = reverse('users_api:signup')
        self.data = {
            'is_age_verified': True,
            'is_terms_accepted': True,
            'name': lorem_ipsum.words(1),
            'last_name': lorem_ipsum.words(1),
            'pwd': '123456@', 'pwd2': '123456@',
            'first_name': lorem_ipsum.words(1),
            'email': '{}@example.com'.format(lorem_ipsum.words(1)),
            'location': {
                'zipcode': '65000', 'street1': lorem_ipsum.words(1),
                'city': lorem_ipsum.words(1), 'state': lorem_ipsum.words(1), 'location_raw': {},
                'lat': 46, 'lng': 30
            },
            'search_criteria': {
                'step4': {'skipped': True},
                'step1': {'hybrid': True, 'indica': False, 'sativa': False},
                'step2': {'effects': [{'value': 1, 'name': 'uplifted'}]},
                'step3': {'skipped': True}}
        }

    @patch.object(EmailService, 'send_confirmation_email', return_value=None)
    def test_signup_without_search_settings(self, _):
        self.data.pop('search_criteria')
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('user' in response.json())
        self.assertEqual(get_user_model().objects.count(), 1)
        self.assertEqual(UserLocation.objects.count(), 1)
        self.assertEqual(UserSearch.objects.count(), 0)

    @patch.object(EmailService, 'send_confirmation_email', return_value=None)
    def test_signup_with_search_settings(self, _):
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('user' in response.json())
        self.assertEqual(get_user_model().objects.count(), 1)
        self.assertEqual(UserLocation.objects.count(), 1)
        self.assertEqual(UserSearch.objects.count(), 1)
        self.assertEqual(UserSearch.objects.first().effects, [{'value': 1, 'name': 'uplifted'}])

    @patch.object(EmailService, 'send_confirmation_email', return_value=None)
    def test_signup_with_not_completed_search_settings(self, _):
        self.data['search_criteria'].pop('step3')
        self.data['search_criteria'].pop('step4')
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('user' in response.json())
        self.assertEqual(get_user_model().objects.count(), 1)
        self.assertEqual(UserLocation.objects.count(), 1)
        self.assertEqual(UserSearch.objects.count(), 0)

    @patch.object(EmailService, 'send_confirmation_email', return_value=None)
    def test_signup_with_blank_username(self, _):
        """
        User try to signup without username and get error message
        """
        self.data.pop('name')
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'error': {'name': ['This field is required.']}})

    @patch.object(EmailService, 'send_confirmation_email', return_value=None)
    def test_signup_empty_form(self, _):
        """
        User submit empty to signup data and get error message
        """
        response = self.client.post(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {
            'error': {'email': ['This field is required.'],
                      'first_name': ['This field is required.'],
                      'last_name': ['This field is required.'],
                      'name': ['This field is required.'],
                      'pwd': ['This field is required.'],
                      'pwd2': ['This field is required.']}})

    @patch.object(EmailService, 'send_confirmation_email', return_value=None)
    def test_signup_is_terms_accepted(self, _):
        """
        User tries to signup without accepting is_terms_accepted and get error message
        """
        self.data.pop('is_terms_accepted')
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'error': {'is_terms_accepted': ['This field is required.']}})

    @patch.object(EmailService, 'send_confirmation_email', return_value=None)
    def test_signup_is_age_verified(self, _):
        """
        User tries to signup without accepting is_age_verified and get error message
        """
        self.data.pop('is_age_verified')
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'error': {'is_age_verified': ['This field is required.']}})

    @patch.object(EmailService, 'send_confirmation_email', return_value=None)
    def test_signup_with_not_unique_username(self, _):
        """
        User try to signup with existing username and get error message
        """
        user = UserFactory()
        self.data['name'] = user.name
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'error': {
            'name': ['There is already an account associated with that user name']}})
