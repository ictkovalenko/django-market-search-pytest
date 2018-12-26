from mock import patch
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from web.es_service import BaseElasticService


class SearchTestCase(APITestCase):
    SUCCESS_RESPONSE = {'hits': {'total': 1, 'hits': [
        {'_source': {'name': 'test', 'removed_date': None}}]}}

    def setUp(self):
        self.url = reverse('search_api:search')

    @patch.object(BaseElasticService, '_request', return_value=SUCCESS_RESPONSE)
    def test_search(self, _):
        response = self.client.get('{}?q={}'.format(self.url, 'a'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['total'], 1)

    @patch.object(BaseElasticService, '_request', return_value=SUCCESS_RESPONSE)
    def test_search_second_page(self, _):
        response = self.client.get('{}?q={}&page=2'.format(self.url, 'a'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['total'], 1)

    @patch.object(BaseElasticService, '_request', return_value={})
    def test_search_without_params(self, _):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {'total': 0, 'list': []})

    @patch.object(BaseElasticService, '_request', return_value={})
    def test_search_with_invalid_params(self, _):
        response = self.client.get('{}?q={}&page=test&size=2000'.format(self.url, 'test'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {'list': [], 'q': 'test',
                                           'similar_vts': {'list': [], 'total': 0}, 'total': 0})

        response = self.client.get('{}?q={}&page=10&size=test'.format(self.url, 'test'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {'list': [], 'q': 'test',
                                           'similar_vts': {'list': [], 'total': 0}, 'total': 0})

        response = self.client.get('{}?q={}&page=10&size='.format(self.url, 'test'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {'list': [], 'q': 'test',
                                           'similar_vts': {'list': [], 'total': 0}, 'total': 0})
