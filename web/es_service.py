import base64
import json
import logging

import requests
from django.conf import settings
from requests import HTTPError

logger = logging.getLogger(__name__)


class BaseElasticService(object):
    '''
    Base ES Service that other apps should inherit from
    '''
    BASE_ELASTIC_URL = settings.ELASTICSEARCH_URL

    # all API endpoints
    URLS = {
        'VT': '/vt',
        'USER_RATINGS': '/user_ratings',
        'BUSINESS_LOCATION': '/business_location'
    }

    HEADERS = {
        'Content-Type': 'application/json',
        'User-Agent': 'Platform',
        'Authorization': 'Basic {0}'.format(bytes.decode(base64.b64encode(
            bytes('{0}:{1}'.format(settings.ELASTICSEARCH_USERNAME, settings.ELASTICSEARCH_PASSWORD), 'utf-8')))),
    }

    METHODS = {
        'GET': 'GET',
        'POST': 'POST',
        'DELETE': 'DELETE',
        'PUT': 'PUT'
    }

    TIMEOUT = 600  # seconds

    def _request(self, method, url, params=None, data=None, json=None):
        """
        Wrapper around requests library - see http://docs.python-requests.org/en/latest/api/#main-interface

        :param method: HTTP verb
        :param url: URL this API endpoint
        :param params: (optional) query params
        :param data:  (optional) dict of data to put into body
        :param json: (optional) data to be converted to json and put into body
        :return: returns json response
        """
        # TODO consider making request non-blocking with https://github.com/kennethreitz/grequests or https://github.com/ross/requests-futures
        r = requests.request(method, url, params=params, data=data, json=json, headers=self.HEADERS,
                             timeout=self.TIMEOUT)
        logger.debug('ES status: {0}'.format(r.status_code))
        r.raise_for_status()
        return r.json()

    def insert(self, index, data):
        """
        inserts a data into ES
        :param data: dictionary of data to insert
        :return: retuns ES success of fail response
        """
        url = '{0}/{1}'.format(self.BASE_ELASTIC_URL, index)
        method = self.METHODS.get('POST')
        resp = self._request(method, url, data=json.dumps(data))

        return resp

    def upsert(self, index, index_type, doc_id, data):
        '''
            Upsert a document
        '''
        url = '{0}/{1}/{2}/{3}/_update'.format(self.BASE_ELASTIC_URL, index, index_type, doc_id)
        method = self.METHODS.get('POST')
        resp = self._request(method, url, data=json.dumps(data))

        return resp

    def parse_bulk_errors(self, resp):
        '''
        ES bulk updates are not atomic, so if one request fails the others will continue.
        This method parses out specific error information from ES response so we can take action
        See https://www.elastic.co/guide/en/elasticsearch/guide/current/bulk.html

        :param resp:
        :return:
        '''
        success = False,
        errors = []

        if resp.get('errors') is False:
            success = True
            return success, errors

        for r in resp.get('items', []):
            # add any non 2XX response to errors list
            if r.get('status') and r.get('status') > 299:
                errors.append(r)

        return success, errors

    def bulk_index(self, data, index=None, index_type=None):
        '''
        Bulk index data
        Make sure data adheres to proper format: https://www.elastic.co/guide/en/elasticsearch/guide/current/bulk.html
        :param data:
        :return:
        '''
        # bulk updates can specify index and index_type as options or contain them in data
        if index is not None and index_type is None:
            url = '{0}/{1}/_bulk'.format(self.BASE_ELASTIC_URL, index)
        elif index is not None and index_type is not None:
            url = '{0}/{1}/{2}/_bulk'.format(self.BASE_ELASTIC_URL, index, index_type)
        else:
            url = '{0}/_bulk'.format(self.BASE_ELASTIC_URL)

        method = self.METHODS.get('POST')
        resp = self._request(method, url, data=data)

        success, errors = self.parse_bulk_errors(resp)

        return {'success': success, 'errors': errors}

    def search(self, data, index=None):
        url = '{0}/{1}/_search'.format(self.BASE_ELASTIC_URL, index)
        method = self.METHODS.get('POST')
        return self._request(method, url, data=json.dumps(data))

    def delete_index(self, index):
        """
        deletes entire ES index
        :param index: the index to delete
        :return: ES response if successfully deleted
        """
        url = '{0}/{1}'.format(self.BASE_ELASTIC_URL, index)
        method = self.METHODS.get('DELETE')

        try:
            return self._request(method, url)
        except HTTPError as e:
            logger.error("[{0}] index does not exist: {1}", index, e)

    def set_alias(self, index, alias):
        '''
        sets alias on a given index
        see: https://www.elastic.co/guide/en/elasticsearch/reference/1.5/indices-aliases.html
        '''
        url = '{0}/_aliases'.format(self.BASE_ELASTIC_URL)
        method = self.METHODS.get('POST')
        alias_query = {
            'actions': [
                {
                    'add': {
                        'index': index,
                        'alias': alias
                    }
                }
            ]
        }
        resp = self._request(method, url, data=json.dumps(alias_query))

        return resp

    def remove_alias(self, index, alias):
        '''
        removes index from a given alias
        see: https://www.elastic.co/guide/en/elasticsearch/reference/1.5/indices-aliases.html
        '''
        url = '{0}/_aliases'.format(self.BASE_ELASTIC_URL)
        method = self.METHODS.get('POST')
        alias_query = {
            'actions': [
                {
                    'remove': {
                        'index': index,
                        'alias': alias
                    }
                }
            ]
        }
        resp = self._request(method, url, data=json.dumps(alias_query))

        return resp

    def delete(self, url, data):
        """
        deletes ES data
        :param index: the url to delete
        :param index: body of delete method
        :return: ES response if successfully deleted
        """
        url = '{0}/{1}'.format(self.BASE_ELASTIC_URL, url)
        method = self.METHODS.get('DELETE')

        resp = self._request(method, url, data=data)

        return resp

    def set_settings(self, index, index_settings):
        """

        :param index:
        :param index_settings:
        :return:
        """
        url = '{0}/{1}'.format(self.BASE_ELASTIC_URL, index)
        method = self.METHODS.get('PUT')
        resp = self._request(method, url, data=json.dumps(index_settings))

        return resp

    def set_mapping(self, index, index_type, mapping_data):
        """
        sets mapping to index
        :param index: index to set mapping to
        :param mapping_data: data schema to map
        :return: ES response
        """
        url = '{0}/{1}/{2}/_mapping'.format(self.BASE_ELASTIC_URL, index, index_type)
        method = self.METHODS.get('PUT')
        resp = self._request(method, url, data=json.dumps(mapping_data))

        return resp
