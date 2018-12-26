import json
from datetime import datetime

from web.businesses.es_serializers import BusinessLocationESSerializer, MenuItemESSerializer
from web.es_service import BaseElasticService
from web.search import es_mappings


class BusinessLocationESService(BaseElasticService):
    def get_business_location_by_db_id(self, db_id):
        url = '{base}{index}/{type}/_search'.format(base=self.BASE_ELASTIC_URL,
                                                    index=self.URLS.get('BUSINESS_LOCATION'),
                                                    type=es_mappings.TYPES.get('business_location'))

        query = {"query": {"match": {"business_location_id": db_id}}}
        es_response = self._request(self.METHODS.get('POST'), url, data=json.dumps(query))
        return es_response

    def save_business_location(self, business_location):
        es_response = self.get_business_location_by_db_id(business_location.id)
        es_location = es_response.get('hits', {}).get('hits', [])

        es_serializer = BusinessLocationESSerializer(business_location)
        data = es_serializer.data
        # regardless of new or update, add auto complete info
        data['location_name_suggest'] = self.generate_autocomplete_data(business_location)

        if len(es_location) > 0:
            existing_source = es_location[0].get('_source')
            self.update_business_location_data(existing_source, data)
            url = '{base}{index}/{type}/{es_id}'.format(base=self.BASE_ELASTIC_URL,
                                                        index=self.URLS.get('BUSINESS_LOCATION'),
                                                        type=es_mappings.TYPES.get('business_location'),
                                                        es_id=es_location[0].get('_id'))
            es_response = self._request(self.METHODS.get('PUT'), url, data=json.dumps(existing_source))
        else:
            data['menu_items'] = []
            data['location'] = {
                "lat": data.get('lat') if data.get('lat') else 0,
                "lon": data.get('lng') if data.get('lng') else 0
            }
            url = '{base}{index}/{type}'.format(base=self.BASE_ELASTIC_URL, index=self.URLS.get('BUSINESS_LOCATION'),
                                                type=es_mappings.TYPES.get('business_location'))
            es_response = self._request(self.METHODS.get('POST'), url, data=json.dumps(data))

        return es_response

    def update_business_location_data(self, existing_data, new_data):
        existing_data['location_name'] = new_data.get('location_name')
        existing_data['manager_name'] = new_data.get('manager_name')
        existing_data['location_email'] = new_data.get('location_email')
        existing_data['dispensary'] = new_data.get('dispensary')
        existing_data['delivery'] = new_data.get('delivery')
        existing_data['grow_house'] = new_data.get('grow_house')
        existing_data['delivery_radius'] = new_data.get('delivery_radius')
        existing_data['street1'] = new_data.get('street1')
        existing_data['city'] = new_data.get('city')
        existing_data['state'] = new_data.get('state')
        existing_data['zip_code'] = new_data.get('zip_code')
        existing_data['location'] = {
            "lat": new_data.get('lat') if new_data.get('lat') else 0,
            "lon": new_data.get('lng') if new_data.get('lng') else 0
        }
        existing_data['location_raw'] = new_data.get('location_raw')
        existing_data['phone'] = new_data.get('phone')
        existing_data['ext'] = new_data.get('ext')
        existing_data['timezone'] = new_data.get('timezone')
        existing_data['removed_by_id'] = new_data.get('removed_by_id')
        existing_data['removed_date'] = new_data.get('removed_date')
        existing_data['created_date'] = new_data.get('created_date')
        existing_data['mon_open'] = new_data.get('mon_open')
        existing_data['mon_close'] = new_data.get('mon_close')
        existing_data['tue_open'] = new_data.get('tue_open')
        existing_data['tue_close'] = new_data.get('tue_close')
        existing_data['wed_open'] = new_data.get('wed_open')
        existing_data['wed_close'] = new_data.get('wed_close')
        existing_data['thu_open'] = new_data.get('thu_open')
        existing_data['thu_close'] = new_data.get('thu_close')
        existing_data['fri_open'] = new_data.get('fri_open')
        existing_data['fri_close'] = new_data.get('fri_close')
        existing_data['sat_open'] = new_data.get('sat_open')
        existing_data['sat_close'] = new_data.get('sat_close')
        existing_data['sun_open'] = new_data.get('sun_open')
        existing_data['sun_close'] = new_data.get('sun_close')
        existing_data['image'] = new_data.get('image')
        existing_data['url'] = new_data.get('url')
        existing_data['urls'] = new_data.get('urls')
        existing_data['location_name_suggest'] = new_data.get('location_name_suggest')

    def generate_autocomplete_data(self, business_location):
        # generate variants of name for suggestion
        input_variants = [business_location.location_name]
        name_words = business_location.location_name.split(' ')
        if len(name_words) > 1:
            for i, name_word in enumerate(name_words):
                if i < len(name_words) - 1:
                    input_variants.append('{0} {1}'.format(name_word, name_words[i + 1]))
                else:
                    input_variants.append(name_word)

        # set business type for context suggestions
        bus_type = []

        if business_location.dispensary:
            bus_type.append('dispensary')

        if business_location.delivery:
            bus_type.append('delivery')

        if business_location.grow_house:
            bus_type.append('grow_house')

        if not business_location.is_searchable():
            bus_type = ['non_searchable']

        return {
            "input": input_variants,
            "weight": 100 - len(input_variants),
            "contexts": {
                "bus_type": bus_type
            }
        }

    def save_menu_item(self, menu_item):
        es_response = self.get_business_location_by_db_id(menu_item.business_location_id)
        es_location = es_response.get('hits', {}).get('hits', [])

        es_serializer = MenuItemESSerializer(menu_item)
        data = es_serializer.data

        if len(es_location) > 0:
            existing_source = es_location[0].get('_source')
            menu_items = existing_source.get('menu_items')
            exist = False

            for mi in menu_items:
                if mi.get('id') == menu_item.id:
                    mi['price_gram'] = data.get('price_gram')
                    mi['price_eighth'] = data.get('price_eighth')
                    mi['price_quarter'] = data.get('price_quarter')
                    mi['price_half'] = data.get('price_half')
                    mi['in_stock'] = data.get('in_stock')
                    mi['removed_date'] = data.get('removed_date')
                    exist = True

            if not exist:
                menu_items.append(data)

            existing_source['menu_items'] = menu_items

            url = '{base}{index}/{type}/{es_id}'.format(base=self.BASE_ELASTIC_URL,
                                                        index=self.URLS.get('BUSINESS_LOCATION'),
                                                        type=es_mappings.TYPES.get('business_location'),
                                                        es_id=es_location[0].get('_id'))

            es_response = self._request(self.METHODS.get('PUT'), url, data=json.dumps(existing_source))
            return es_response

        return None

    def delete_menu_item(self, menu_item):
        es_response = self.get_business_location_by_db_id(menu_item.business_location_id)
        es_location = es_response.get('hits', {}).get('hits', [])

        if len(es_location) > 0:
            existing_source = es_location[0].get('_source')
            menu_items = existing_source.get('menu_items')

            for mi in menu_items:
                if mi.get('id') != menu_item.id:
                    mi['removed_date'] = datetime.now().isoformat()

            existing_source['menu_items'] = menu_items

            url = '{base}{index}/{type}/{es_id}'.format(base=self.BASE_ELASTIC_URL,
                                                        index=self.URLS.get('BUSINESS_LOCATION'),
                                                        type=es_mappings.TYPES.get('business_location'),
                                                        es_id=es_location[0].get('_id'))

            es_response = self._request(self.METHODS.get('PUT'), url, data=json.dumps(existing_source))
            return es_response

        return None

    def delete_business_location(self, db_id):
        es_response = self.get_business_location_by_db_id(db_id)
        data = es_response.get('hits', {}).get('hits', [{}])
        if not data:
            return

        es_id = data[0].get('_id')
        url = '{base}{index}/{type}/{db_id}'.format(base=self.BASE_ELASTIC_URL,
                                                    index=self.URLS.get('BUSINESS_LOCATION'),
                                                    type=es_mappings.TYPES.get('business_location'),
                                                    db_id=es_id)

        method = self.METHODS.get('DELETE')

        resp = self._request(method, url, data=None)

        return resp

    def lookup_location(self, lookup_query):
        method = self.METHODS.get('POST')
        url = '{base}{index}/{type}/_search'.format(
            base=self.BASE_ELASTIC_URL,
            index=self.URLS.get('BUSINESS_LOCATION'),
            type=es_mappings.TYPES.get('business_location')
        )

        query = {
            "_source": ["business_location_id", "urls.dispensary", "location_name"],
            "query": {
                "bool": {
                    "should": [
                        {"match": {'dispensary': True}},
                        {"match": {'delivery': True}},
                    ],
                    "must_not": {
                        "exists": {"field": "removed_date"}
                    },
                    "minimum_should_match": '0<80%'
                }
            },
            "suggest": {
                "name_suggestion": {
                    "text": lookup_query,
                    "completion": {
                        "field": "location_name_suggest",
                        "size": 10,
                        "fuzzy": {
                            "fuzziness": 1
                        }
                    }
                }
            }
        }

        es_response = self._request(method, url, data=json.dumps(query))
        suggests = es_response.get('suggest', {}).get('name_suggestion', [])
        payloads = []

        if len(suggests) > 0:
            suggestion = suggests[0]
            for option in suggestion.get('options'):
                source = option.get('_source')
                payloads.append({
                    'id': source['urls'].get('dispensary'),
                    'name': source['location_name'],
                    'type': 'href'
                })
        return payloads
