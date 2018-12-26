import json

from web.es_service import BaseElasticService
from web.search import es_mappings
from web.search.serializers import VtESSerializer


class VtESService(BaseElasticService):
    def get_vt_by_db_id(self, db_vt_id):
        url = '{base}{index}/{type}/_search'.format(base=self.BASE_ELASTIC_URL,
                                                    index=self.URLS.get('VT'),
                                                    type=es_mappings.TYPES.get('vt'))
        query = {
            "query": {
                "match": {
                    "id": db_vt_id
                }
            }
        }

        es_response = self._request(self.METHODS.get('POST'), url, data=json.dumps(query))
        return es_response

    def get_vt_review_by_db_id(self, db_vt_review_id):
        url = '{base}{index}/{type}/_search'.format(base=self.BASE_ELASTIC_URL,
                                                    index=self.URLS.get('VT'),
                                                    type=es_mappings.TYPES.get('vt_review'))
        query = {
            "query": {
                "match": {
                    "id": db_vt_review_id
                }
            }
        }

        es_response = self._request(self.METHODS.get('POST'), url, data=json.dumps(query))
        return es_response

    def save_vt_review(self, data, review_db_id, parent_vt_db_id):
        es_response = self.get_vt_review_by_db_id(review_db_id)
        es_review = es_response.get('hits', {}).get('hits', [])
        es_response = self.get_vt_by_db_id(parent_vt_db_id)
        es_vt = es_response.get('hits', {}).get('hits', [])

        if len(es_review) > 0:
            url = '{base}{index}/{type}/{es_id}?parent={parent}'.format(base=self.BASE_ELASTIC_URL,
                                                                        index=self.URLS.get('VT'),
                                                                        type=es_mappings.TYPES.get('vt_review'),
                                                                        es_id=es_review[0].get('_id'),
                                                                        parent=es_vt[0].get('_id'))
            es_response = self._request(self.METHODS.get('PUT'), url, data=json.dumps(data))
        else:
            url = '{base}{index}/{type}?parent={parent}'.format(base=self.BASE_ELASTIC_URL,
                                                                index=self.URLS.get('VT'),
                                                                type=es_mappings.TYPES.get('vt_review'),
                                                                parent=es_vt[0].get('_id'))
            es_response = self._request(self.METHODS.get('POST'), url, data=json.dumps(data))

        return es_response

    def save_vt(self, vt):
        es_response = self.get_vt_by_db_id(vt.id)
        es_vts = es_response.get('hits', {}).get('hits', [])
        es_serializer = VtESSerializer(instance=vt)
        data = es_serializer.data

        if len(es_vts) > 0:
            es_vt = es_vts[0]
            es_vt_source = es_vt.get('_source')
            es_vt_source.update(data)

            url = '{base}{index}/{type}/{es_id}'.format(base=self.BASE_ELASTIC_URL, index=self.URLS.get('VT'),
                                                        type=es_mappings.TYPES.get('vt'),
                                                        es_id=es_vt.get('_id'))
            print('--- updating')
            print(es_vt_source['removed_date'], vt.name)
            es_response = self._request(self.METHODS.get('PUT'), url, data=json.dumps(es_vt_source))
        else:
            data['removed_by_id'] = data.get('removed_by')
            data.pop('removed_by', None)

            url = '{base}{index}/{type}'.format(base=self.BASE_ELASTIC_URL, index=self.URLS.get('VT'),
                                                type=es_mappings.TYPES.get('vt'))
            es_response = self._request(self.METHODS.get('POST'), url, data=json.dumps(data))

        return es_response

    def delete_vt(self, vt_id):
        es_response = self.get_vt_by_db_id(vt_id)
        es_vts = es_response.get('hits', {}).get('hits', [])

        if len(es_vts) > 0:
            es_vt = es_vts[0]
            url = '{base}{index}/{type}/{es_id}'.format(base=self.BASE_ELASTIC_URL, index=self.URLS.get('VT'),
                                                        type=es_mappings.TYPES.get('vt'),
                                                        es_id=es_vt.get('_id'))
            es_response = self._request(self.METHODS.get('DELETE'), url)
            return es_response
