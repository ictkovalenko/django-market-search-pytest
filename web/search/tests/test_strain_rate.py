from django.utils import lorem_ipsum
from mock import patch
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from web.es_service import BaseElasticService
from web.search.models import VtReview
from web.search.tests.factories import VtFactory
from web.users.tests.factories import UserFactory


class SearchTestCase(APITestCase):
    SUCCESS_RESPONSE = {'hits': {'total': 1, 'hits': [
        {'_source': {'name': 'test', 'removed_date': None}}]}}

    def setUp(self):
        self.user = UserFactory()
        self.vt = VtFactory()
        self.url = reverse('search_api:vt_rate', args=(self.vt.pk,))
        self.data = {
            'rating': 5,
            'review': 'test'
        }

    @patch.object(BaseElasticService, '_request', return_value=SUCCESS_RESPONSE)
    def test_rate(self, _):
        """
        User successfully create review
        """
        self.client.force_login(self.user)
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        review = VtReview.objects.first()
        self.assertEqual(VtReview.objects.count(), 1)
        self.assertEqual(review.rating, self.data['rating'])
        self.assertEqual(review.review, '<p>{}</p>\n'.format(self.data['review']))
        self.assertFalse(review.review_approved)

    @patch.object(BaseElasticService, '_request', return_value=SUCCESS_RESPONSE)
    def test_rate_without_review(self, _):
        """
        User successfully create review
        """
        self.data.pop('review')
        self.client.force_login(self.user)
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        review = VtReview.objects.first()
        self.assertEqual(VtReview.objects.count(), 1)
        self.assertEqual(review.rating, self.data['rating'])
        self.assertEqual(review.review, '')
        self.assertTrue(review.review_approved)

    @patch.object(BaseElasticService, '_request', return_value=SUCCESS_RESPONSE)
    def test_rate_not_existing_vt(self, _):
        """
        User try to create review for not existing vt and got 404 error
        """
        self.url = reverse('search_api:vt_rate', args=(self.vt.pk + 1000,))
        self.client.force_login(self.user)
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(VtReview.objects.count(), 0)

    @patch.object(BaseElasticService, '_request', return_value={})
    def test_wrong_data(self, _):
        """
        User submit wrong data and got error message
        """
        self.client.force_login(self.user)
        self.data['review'] = lorem_ipsum.words(count=500)
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(VtReview.objects.count(), 0)
        self.assertEqual(response.json(), {'review': ['Ensure this field has no more than 500 characters.']})

    @patch.object(BaseElasticService, '_request', return_value=SUCCESS_RESPONSE)
    def test_empty_data(self, _):
        """
        User submit empty data
        """
        self.client.force_login(self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(VtReview.objects.count(), 0)
        self.assertEqual(response.json(), {'rating': ['This field is required.']})
