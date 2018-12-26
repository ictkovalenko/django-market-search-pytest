import random

import pytz
from django.utils import lorem_ipsum
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from web.users.models import GENDER
from web.users.tests.factories import UserFactory, TEST_USER_PASSWORD


class UserDetailTestCase(APITestCase):

    def setUp(self):
        self.user = UserFactory()
        self.url = reverse('users_api:user-detail', args=(self.user.pk,))
        self.data = {
            'name': lorem_ipsum.words(1),
            'last_name': lorem_ipsum.words(1),
            'first_name': lorem_ipsum.words(1),
            'email': '{}@example.com'.format(lorem_ipsum.words(1)),
            'birth_month': 'Jan', 'birth_day': 10, 'birth_year': 1989,
            'gender': GENDER[1][0],
            'timezone': random.choice(pytz.common_timezones),
            'location': {
                'zipcode': '65000', 'street1': lorem_ipsum.words(1),
                'city': lorem_ipsum.words(1), 'state': lorem_ipsum.words(1), 'location_raw': {},
                'lat': 46, 'lng': 30
            }
        }

    def test_update_user_detail(self):
        """
        User successfully update his account
        """
        name = self.user.name
        self.client.login(username=self.user.email, password=TEST_USER_PASSWORD)
        response = self.client.put(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        for field in ['last_name', 'first_name', 'email',
                      'birth_month', 'birth_day', 'birth_year', 'gender', 'timezone']:
            self.assertEqual(getattr(self.user, field), self.data[field])
        self.assertEqual(self.user.name, name)

    def test_update_user_detail_without_name(self):
        """
        User successfully update his account
        """
        self.user.name = ''
        self.user.save()
        self.client.login(username=self.user.email, password=TEST_USER_PASSWORD)
        response = self.client.put(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        for field in ['name', 'last_name', 'first_name', 'email',
                      'birth_month', 'birth_day', 'birth_year', 'gender', 'timezone']:
            self.assertEqual(getattr(self.user, field), self.data[field])

    def test_not_owner(self):
        """
        User tries to update account of another user and gets error message
        """
        user = UserFactory()
        self.client.login(username=user.email, password=TEST_USER_PASSWORD)
        response = self.client.put(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous(self):
        """
        Anonymous tries to update his account and gets error
        """
        response = self.client.put(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_empty_data(self):
        """
        User make request with empty data, user's name and email stay same
        """
        email = self.user.email
        name = self.user.name
        self.client.login(username=self.user.email, password=TEST_USER_PASSWORD)
        response = self.client.put(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'email': ['This field is required.']})
        self.user.refresh_from_db()
        self.assertEqual(email, self.user.email)
        self.assertEqual(name, self.user.name)

    def test_empty_data_values(self):
        """
        User make request with empty data values, user's name and email stay same
        """
        self.data = {
            'name': '',
            'last_name': '',
            'first_name': '',
            'email': '',
            'birth_month': '', 'birth_day': '', 'birth_year': '',
            'gender': ''
        }

        self.client.login(username=self.user.email, password=TEST_USER_PASSWORD)
        response = self.client.put(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'email': ['This field may not be blank.']})

        self.data.pop('email')
        response = self.client.put(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'email': ['This field is required.']})

        self.data['email'] = self.user.email
        response = self.client.put(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_birthday(self):
        """
        User does not send full birthday date and get error
        """
        data = {
            'email': '{}@example.com'.format(lorem_ipsum.words(1)),
            'birth_month': 'Jan'
        }
        self.client.login(username=self.user.email, password=TEST_USER_PASSWORD)
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'birth_day': ['This field is required.']})

        data = {
            'email': '{}@example.com'.format(lorem_ipsum.words(1)),
            'birth_month': 'Jan', 'birth_day': 10
        }
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'birth_year': ['This field is required.']})

        data = {
            'birth_month': '', 'birth_day': '', 'birth_year': '',
            'email': '{}@example.com'.format(lorem_ipsum.words(1))
        }
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {'birth_day': None,
                                           'birth_month': None,
                                           'birth_year': None,
                                           'email': data['email'],
                                           'first_name': self.user.first_name,
                                           'gender': self.user.gender,
                                           'last_name': self.user.last_name,
                                           'name': self.user.name,
                                           'timezone': self.user.timezone})

    def test_gender(self):
        self.client.login(username=self.user.email, password=TEST_USER_PASSWORD)
        data = {'gender': '', 'email': '{}@example.com'.format(lorem_ipsum.words(1))}
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(response.json(), {'birth_day': None,
                                           'birth_month': None,
                                           'birth_year': None,
                                           'email': data['email'],
                                           'first_name': self.user.first_name,
                                           'gender': '',
                                           'last_name': self.user.last_name,
                                           'name': self.user.name,
                                           'timezone': self.user.timezone})

    def test_email_duplicate(self):
        user = UserFactory()
        self.data['email'] = user.email

        self.client.login(username=self.user.email, password=TEST_USER_PASSWORD)
        response = self.client.put(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'email': ['There is already an account associated with that email address']})

    def test_username_duplicate(self):
        self.user.name = ''
        self.user.save()

        user = UserFactory()
        self.data['name'] = user.name

        self.client.login(username=self.user.email, password=TEST_USER_PASSWORD)
        response = self.client.put(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'name': ['There is already an account associated with that user name']})
