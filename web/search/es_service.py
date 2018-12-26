import json

from django.db.models import Q
from django.template.defaultfilters import slugify

from web.businesses.api.services import get_open_closed, get_location_rating
from web.common.utils import PythonJSONEncoder
from web.es_service import BaseElasticService
from web.search import es_mappings
from web.search.api.serializers import VtSearchSerializer
from web.search.es_script_score import ADVANCED_SEARCH_SCORE, SRX_RECOMMENDATION_SCORE, CHECK_DELIVERY_RADIUS
from web.search.models import VtImage
from web.system.models import SystemProperty


class SearchElasticService(BaseElasticService):

    def _transform_vt_results(self, results, current_user=None, result_filter=None, include_locations=True,
                                  is_similar=False, similar_vt_id=None):
        """
        :param results:
        :return:
        """
        vts = results.get('hits', {}).get('hits', [])
        total = results.get('hits', {}).get('total', 0)
        processed_results = []

        vt_ratings = {}
        vt_rating_buckets = results.get('aggregations', {}).get('vt_rating', {}).get('buckets', [])
        for b in vt_rating_buckets:
            vt_ratings[b.get('key')] = b.get('child_rating').get('avg_rating').get('value')

        to_transform = []
        if is_similar:
            start_index = -1
            for index, s in enumerate(vts + vts[:5]):
                source = s.get('_source', {})
                if int(source.get('id')) == int(similar_vt_id):
                    start_index = index
                    continue

                if start_index > -1 and len(to_transform) < 5 and not source.get('removed_date') and not source.get('you_may_also_like_exclude'):
                    to_transform.append(s)
        else:
            to_transform = vts

        for s in to_transform:
            source = s.get('_source', {})
            rating = vt_ratings.get(source.get('id'))
            vt_image = VtImage.objects.filter(vt=source.get('id'), is_approved=True)\
                .exclude(Q(image__isnull=True) | Q(image='')).first()
            srx_score = int(round(s.get('_score') or 0))

            if include_locations:
                dispensaries = self.get_locations(
                    source.get('id'), 'dispensary', current_user, only_active=True)
                dispensaries = self.transform_location_results(dispensaries, source.get('id'))

                deliveries = self.get_locations(
                    source.get('id'), 'delivery', current_user, only_active=True)
                deliveries = self.transform_location_results(deliveries, source.get('id'))
            else:
                dispensaries = []
                deliveries = []

            if not source.get('removed_date'):
                processed_results.append({
                    'id': source.get('id'),
                    'name': source.get('name'),
                    'vt_slug': source.get('vt_slug'),
                    'variety': source.get('variety'),
                    'category': source.get('category'),
                    'rating': "{0:.2f}".format(round(rating, 2)) if rating else 'Not Rated',
                    'image_url': vt_image.image.url if vt_image and vt_image.image else None,
                    'match_percentage': srx_score if srx_score <= 100 else 100,
                    'deliveries': deliveries,
                    'locations': dispensaries,
                    'cup_winner': source.get('cup_winner'),
                    'cannabinoids': source.get('cannabinoids')
                })

        return {
            'list': processed_results,
            'total': total
        }

    def get_locations(self, vt_id=None, location_type=None, current_user=None,
                      order_field="distance", order_dir="asc", size=None, only_active=False):

        method = self.METHODS.get('GET')
        url = '{0}{1}{2}'.format(self.BASE_ELASTIC_URL, self.URLS.get('BUSINESS_LOCATION'), '/_search')

        if size:
            url += '?size={0}'.format(size)

        filter_query = {}
        should_query = {}
        script_fields = {}
        params = {}

        if current_user:
            location = current_user.get_location()
            params = dict(lat=location and location.lat or 0, lon=location and location.lng or 0)
            proximity = location_type in ('dispensary', 'all') and current_user.proximity

            if not proximity:
                proximity = SystemProperty.objects.max_delivery_radius()

            if location_type == 'delivery':
                filter_query = {
                    "script": {
                        "script": {
                            "inline": CHECK_DELIVERY_RADIUS,
                            "lang": "painless",
                            "params": params
                        }
                    }
                }
            elif location_type == 'all':

                script_fields = {
                    "is_delivery": {
                        "script": {
                            "lang": "painless",
                            "params": params,
                            "inline": CHECK_DELIVERY_RADIUS
                        }
                    },
                }

                should_query = [
                    {"script": {
                        "script": {
                            "inline": CHECK_DELIVERY_RADIUS,
                            "lang": "painless",
                            "params": params
                        }
                    }},
                    {"bool": {
                        "must": [
                            {
                                "geo_distance": {
                                    "distance": "{0}mi".format(proximity),
                                    "distance_type": "plane", "location": params
                                }
                            },
                            {"match": {'dispensary': True}}
                        ]
                    }}
                ]
            else:
                filter_query = {
                    "geo_distance": {
                        "distance": "{0}mi".format(proximity),
                        "distance_type": "plane", "location": params
                    }
                }

        bool_menu_items = {"must_not": [{"exists": {"field": "menu_items.removed_date"}}],
                           'must': [{"term": {"menu_items.in_stock": True}}]}

        if vt_id:
            bool_menu_items["must"].append({"match": {"menu_items.vt_id": vt_id}})

        must_query = [{"nested": {"path": "menu_items", "query": {"bool": bool_menu_items}}}]

        if location_type in ('dispensary', 'delivery'):
            must_query.append({"match": {location_type: True}})

        must_not_query = {}
        if only_active:
            must_not_query.update({"exists": {"field": "removed_date"}})

        # Sort
        sort_query = []
        if order_field != 'distance' and order_field != 'rating' and not order_field.startswith('menu_items'):
            sort_query.append({order_field: {"order": order_dir}})

        if order_field.startswith('menu_items'):
            order_field_bool = {
                "must_not": [{"exists": {"field": "menu_items.removed_date"}}],
                'must': [{"term": {"menu_items.in_stock": True}}]
            }

            if vt_id:
                order_field_bool["must"].append({"match": {"menu_items.vt_id": vt_id}})
            sort_query.append({order_field: {"order": order_dir, "nested_path": "menu_items",
                                             "nested_filter": {"bool": order_field_bool}}})

        if params:
            if order_field == 'distance':
                sort_query.append({"_geo_distance": {
                    "location": params, "order": order_dir if order_dir else "asc",
                    "unit": "mi", "distance_type": "plane"}})
            else:
                sort_query.append({"_geo_distance": {
                    "location": params, "order": "asc", "unit": "mi", "distance_type": "plane"}})

        query = {
            "_source": ['menu_items', 'business_id', 'business_location_id', 'category', 'slug_name', 'city',
                        'state', 'location_name',
                        'mon_open', 'tue_open', 'wed_open', 'thu_open', 'fri_open', 'sat_open', 'sun_open',
                        'mon_close', 'tue_close', 'wed_close', 'thu_close', 'fri_close', 'sat_close', 'sun_close'],
            "query": {
                "bool": {
                    "must": must_query,
                    "must_not": must_not_query,
                    "filter": filter_query,
                    "should": should_query,
                    "minimum_should_match": '0<80%',
                }
            },
            'script_fields': script_fields,
            "sort": sort_query
        }

        return self._request(method, url, data=json.dumps(query))

    def transform_location_results(self, es_response, vt_id=None):
        locations = es_response.get('hits', {}).get('hits', [])
        processed_results = []
        for l in locations:
            s = l.get('_source')
            is_delivery = l.get('fields', {}).get('is_delivery', [None])[0]
            sort = l.get('sort')
            distance = sort[1] if sort and len(sort) >= 2 else sort[0] if sort and len(sort) == 1 else None
            menu_item_id = None
            in_stock = False
            price_gram = None
            price_half = None
            price_quarter = None
            price_eighth = None

            for mi in s.get('menu_items', []):
                if int(mi.get('vt_id')) == int(vt_id):
                    menu_item_id = mi.get('id')
                    in_stock = mi.get('in_stock')
                    price_gram = mi.get('price_gram')
                    price_half = mi.get('price_half')
                    price_quarter = mi.get('price_quarter')
                    price_eighth = mi.get('price_eighth')

            processed_results.append({
                'business_id': s.get('business_id'), 'location_id': s.get('business_location_id'),
                'category': s.get('category', 'dispensary'),
                'slug_name': s.get('slug_name'),
                'city_slug': slugify(s.get('city')),
                'state': s.get('state'),
                'location_name': s.get('location_name'), 'distance': distance,
                'menu_item_id': menu_item_id, 'in_stock': in_stock,
                'price_gram': price_gram, 'price_half': price_half,
                'price_quarter': price_quarter, 'price_eighth': price_eighth,
                'open': get_open_closed(s) == 'Opened',
                'is_delivery': is_delivery if is_delivery is not None else s.get('delivery'),
                'rating': get_location_rating(s.get('business_location_id'))
            })

        return processed_results

    def query_vts_by_name(self, query, size=50, start_from=0):
        """
        Get stains by name in a 'name contains' manner

        :param query: part of the word to search for
        :param size: size of returned data
        :param start_from: number of entity to start search from
        :return: { 'list': [], 'total': 0 }
        """

        if start_from is None:
            start_from = 0

        method = self.METHODS.get('GET')
        url = '{0}{1}{2}{3}{4}{5}'.format(
            self.BASE_ELASTIC_URL,
            self.URLS.get('VT'),
            '/_search?size=', size,
            '&from=', start_from)

        # build query dict
        query = {
            'query': {
                'match': {
                    'name': query.lower()
                }
            }
        }

        q = self._request(method, url, data=json.dumps(query))

        # remove extra info returned by ES and do any other necessary transforms
        results = self._transform_vt_results(q)

        return results

    def query_user_review_srx_score(self, criteria, vt_id=None, user_id=None):
        method = self.METHODS.get('GET')
        url = '{base}{index}/{type}/_search'.format(base=self.BASE_ELASTIC_URL, index=self.URLS.get('USER_RATINGS'),
                                                    type=es_mappings.TYPES.get('vt_rating'))

        query = self.build_srx_score_user_review_es_query(criteria, vt_id, user_id)

        es_response = self._request(method, url, data=json.dumps(query))

        # remove extra info returned by ES and do any other necessary transforms
        results = self.transform_user_review_results(es_response)
        return results

    def build_srx_score_user_review_es_query(self, criteria, vt_id, user_id):
        effects_data = self.parse_criteria_data(criteria.get('effects'))
        benefits_data = self.parse_criteria_data(criteria.get('benefits'))
        side_effects_data = self.parse_criteria_data(criteria.get('side_effects'))

        vt_filter = {
            "bool": {
                "must": [
                    {"term": {"vt_id": vt_id}},
                    {"term": {"user_id": user_id}}
                ],
                "must_not": {
                    "exists": {"field": "removed_date"}
                }
            }
        }

        return {
            "query": {
                "function_score": {
                    "query": vt_filter,
                    "functions": [{
                        "script_score": {
                            "script": {
                                "lang": "painless",
                                "params": {
                                    "effectSum": effects_data.get('sum'),
                                    "benefitSum": benefits_data.get('sum'),
                                    "userEffects": effects_data.get('data'),
                                    "userBenefits": benefits_data.get('data'),
                                    "userNegEffects": side_effects_data.get('data')
                                },
                                "inline": SRX_RECOMMENDATION_SCORE
                            }
                        }
                    }]
                }
            }
        }

    def transform_user_review_results(self, results):
        vts = results.get('hits', {}).get('hits', [])
        score = int(round(vts[0].get('_score'))) if len(vts) > 0 else 'n/a'

        if score != 'n/a':
            return score if score <= 100 else 100
        else:
            return score

    def query_vt_srx_score(self, criteria, size=50, start_from=0, vt_ids=None, current_user=None,
                               result_filter=None, include_locations=True, is_similar=False, similar_vt_id=None):
        """
        Return vts ranked by SRX score
        """
        if start_from is None:
            start_from = 0

        method = self.METHODS.get('GET')
        url = '{base}{index}/{type}/_search?size={size}&from={start_from}'.format(
            base=self.BASE_ELASTIC_URL,
            index=self.URLS.get('VT'),
            type=es_mappings.TYPES.get('vt'),
            size=size,
            start_from=start_from
        )

        if result_filter == 'all':
            query = self.build_srx_score_es_query(criteria, vt_ids)
        elif result_filter == 'local':

            location = current_user.get_location()
            proximity = current_user and current_user.proximity or SystemProperty.objects.max_delivery_radius()
            params = dict(lat=location and location.lat or 0, lon=location and location.lng or 0)

            subquery = {
                "nested": {
                    "path": "locations",
                    "query": {
                        "bool": {
                            "must": {
                                "match": {
                                    "locations.dispensary": True
                                }
                            },
                            "filter": {
                                "geo_distance": {
                                    "locations.location": params,
                                    "distance_type": "plane",
                                    "distance": "{}mi".format(proximity)
                                }
                            }
                        }
                    }
                }
            }
            query = self.build_srx_score_es_query(criteria, None, subquery)
            query["_source"] = ["name", "effects", "benefits", "side_effects", "id", "vt_slug",
                                "variety", "category", "cup_winner", "cannabinoids"]

        elif result_filter == 'delivery':
            location = current_user.get_location()
            params = dict(lat=location and location.lat or 0, lon=location and location.lng or 0)
            subquery = {
                "nested": {
                    "path": "locations",
                    "query": {
                        "bool": {
                            "must": {
                                "script": {
                                    "script": {
                                        "inline": """
                                            def delivery_radius = doc['locations.delivery_radius'].value ?: 0; 
                                            return doc['locations.delivery'].value == true && delivery_radius >= 
                                                doc['locations.location'].planeDistanceWithDefault(
                                                  params.lat, params.lon, 0) * 0.000621371
                                        """,
                                        "lang": "painless",
                                        "params": params
                                    }
                                }
                            }
                        }
                    }
                }
            }

            query = self.build_srx_score_es_query(criteria, None, subquery)
        else:
            query = self.build_srx_score_es_query(criteria, vt_ids)

        es_response = self._request(method, url, data=json.dumps(query))
        return self._transform_vt_results(es_response, current_user,
                                              include_locations=include_locations, is_similar=is_similar,
                                              similar_vt_id=similar_vt_id)

    def build_srx_score_es_query(self, criteria, vt_ids=None, nested_query=None):
        criteria_vt_types = self.parse_criteria_vts(criteria.get('vt_types'))
        effects_data = self.parse_criteria_data(criteria.get('effects'))
        benefits_data = self.parse_criteria_data(criteria.get('benefits'))
        side_effects_data = self.parse_criteria_data(criteria.get('side_effects'))

        query_filter = []
        if vt_ids:
            query_filter.append({"terms": {"id": vt_ids}})

        if nested_query:
            query_filter.append(nested_query)

        if criteria_vt_types:
            query_filter.append({"terms": {"variety": criteria_vt_types}})

        vt_filter = {"bool": {"must_not": {"exists": {"field": "removed_date"}}}}
        if query_filter:
            vt_filter["bool"]["must"] = query_filter

        vt_aggs = {
            "vt_rating": {
                "terms": {
                    "field": "id",
                    "order": {
                        "srx_score": "desc"
                    }
                },
                "aggs": {
                    "child_rating": {
                        "children": {
                            "type": "vt_review"
                        },
                        "aggs": {
                            "avg_rating": {
                                "avg": {
                                    "field": "rating"
                                }
                            }
                        }
                    },
                    "srx_score": {
                        "max": {
                            "script": {
                                "inline": "_score",
                                "lang": "painless"
                            }
                        }
                    }
                }
            }
        }
        return {
            "aggs": vt_aggs,
            "query": {
                "function_score": {
                    "query": vt_filter,
                    "functions": [{
                        "script_score": {
                            "script": {
                                "lang": "painless",
                                "params": {
                                    "effectSum": effects_data.get('sum'),
                                    "benefitSum": benefits_data.get('sum'),
                                    "userEffects": effects_data.get('data'),
                                    "userBenefits": benefits_data.get('data'),
                                    "userNegEffects": side_effects_data.get('data')
                                },
                                "inline": SRX_RECOMMENDATION_SCORE
                            }
                        }
                    }]
                }
            }
        }

    def parse_criteria_data(self, criteria):
        data = {}
        data_sum = 0

        if criteria and len(criteria) > 0 and criteria != 'skipped':
            for e in criteria:
                data_sum += e.get('value')
                data[e.get('name')] = e.get('value')

        return {
            'data': data,
            'sum': data_sum
        }

    def parse_criteria_vts(self, criteria):
        if criteria == 'skipped':
            vts = False
        else:
            vts = [k.lower() for k, v in criteria.items() if v]

        return vts

    def lookup_vt(self, query):
        method = self.METHODS.get('POST')
        url = '{base}{index}/{type}/_search'.format(
            base=self.BASE_ELASTIC_URL,
            index=self.URLS.get('VT'),
            type=es_mappings.TYPES.get('vt')
        )

        if ' ' in query:
            query = {
                "_source": ["id", "name", "variety", "vt_slug", "removed_date"],
                "query": {
                    "match": {
                        "name": {
                            "query": query,
                            "fuzziness": 1
                        }
                    }
                }
            }

            es_response = self._request(method, url, data=json.dumps(query))
            results = self._transform_query_results(es_response)
        else:
            query = {
                "_source": ["id", "name", "variety", "vt_slug", "removed_date"],
                "suggest": {
                    "name_suggestion": {
                        "text": query,
                        "completion": {
                            "field": "name_suggest",
                            "size": 25,
                            "fuzzy": {
                                "fuzziness": 1
                            }
                        }
                    }
                }
            }

            es_response = self._request(method, url, data=json.dumps(query))
            results = self._transform_suggest_results(es_response)

        return results

    def lookup_vt_by_name(self, lookup_query, current_user, size=24, start_from=0):
        """
        Get stains by name in a 'name contains' manner, similar vts using more_like_this query

        :param lookup_query: part of the word to search for
        :param size: size of returned data
        :param start_from: number of entity to start search from
        :return: { 'list': [], 'total': 0, 'q': <lookup_query>, 'similar_vts'}
        """

        if start_from is None:
            start_from = 0

        method = self.METHODS.get('GET')
        url = '{base}{index}/{type}/_search?size={size}&from={start_from}'.format(
            base=self.BASE_ELASTIC_URL,
            index=self.URLS.get('VT'),
            type=es_mappings.TYPES.get('vt'),
            size=size,
            start_from=start_from
        )

        location = current_user.get_location()
        proximity = current_user.proximity
        sort_query = []
        for item in [
            VtSearchSerializer.BEST_MATCH, VtSearchSerializer.NAME, VtSearchSerializer.LOCATION,
            VtSearchSerializer.PRICE, VtSearchSerializer.MAX_PRICE_GRAM, VtSearchSerializer.PRICE_EIGHTH,
            VtSearchSerializer.MAX_PRICE_EIGHTH, VtSearchSerializer.PRICE_QUARTER,
            VtSearchSerializer.MAX_PRICE_QUARTER
        ]:
            sort_query.append(
                VtSearchSerializer.SORT_FIELDS[item](
                    lat=location and location.lat or 0, lon=location and location.lng or 0,
                    proximity=proximity)
            )

        # build query dict
        query = {
            'sort': sort_query,
            'query': {
                "bool": {
                    "must": {
                        'match': {
                            'name.exact': lookup_query
                        }
                    },
                    "must_not": {
                        "exists": {"field": "removed_date"}
                    }
                }
            }
        }
        q = self._request(method, url, data=json.dumps(query))
        # remove extra info returned by ES and do any other necessary transforms
        results = self._transform_search_results(q)

        query = {
            'sort': sort_query,
            "query": {
                "bool": {
                    "must": {
                        "match": {"name": lookup_query}
                    },
                    "must_not": [
                        {"match": {"name.exact": lookup_query}},
                        {"exists": {"field": "removed_date"}}
                    ]
                }
            }
        }

        similar_vts = self._request(method, url, data=json.dumps(query))
        similar_vts_results = self._transform_search_results(similar_vts)

        return {'q': lookup_query, 'similar_vts': similar_vts_results, **results}

    def advanced_search(self, lookup_query, current_user, size=24, start_from=0):
        """
        Search Algo:
        Class match: 20 points for matching vts (a max of 20 points can be assigned for this category)
        Cannabinoids: 100 points per matching cannabiniod;
        if the delta between actual value and desired range is more than 75% of actual value,
        subtract 75% of assigned points, per cannabinoid.
        If delta is 55%-74%, subtract 50% of points.
        If delta is 20%-54%, subtract 25% of points. (no max per category)

          total += 100
          if actual > max:
            delta = actual - max
          else:
            delta = actual - min

          if delta >= actual * 0.75:
            total = total * 0.25
          elif delta >= actual * 0.55:
            total = total * 0.50
          elif delta >= actual * 0.20:
            total = total * 0.75

        Terpenes: 20 points per matching terpene
        Clean: 40 points
        Indoor: 15 points
        Cup: 10 points

        :param lookup_query: dict with ranges for the cannabinoids,
               boolean values for the terpenes, variety, cup, clean and indoor
        :param size: size of returned data
        :param start_from: number of entity to start search from
        :return: { 'list': [], 'total': 0 }
        """
        if start_from is None:
            start_from = 0

        method = self.METHODS.get('GET')
        url = '{base}{index}/{type}/_search'.format(
            base=self.BASE_ELASTIC_URL,
            index=self.URLS.get('VT'),
            type=es_mappings.TYPES.get('vt')
        )

        must_query = []
        for field in ('is_clean', 'is_indoor'):
            if lookup_query.get(field):
                must_query.append({"term": {field: lookup_query[field]}})

        if lookup_query.get('variety'):
            must_query.append({"terms": {'variety': lookup_query['variety']}})

        for terpene in VtSearchSerializer.TERPENES:
            if lookup_query.get(terpene):
                must_query.append({
                    "range": {
                        'terpenes.{}'.format(terpene): {
                            "gt": 0
                        }
                    }
                })

        for cannabinoid in VtSearchSerializer.CANNABINOIDS:
            if '{}_from'.format(cannabinoid) in lookup_query or '{}_to'.format(cannabinoid) in lookup_query:
                must_query.append({
                    "range": {
                        'cannabinoids.{}'.format(cannabinoid): {
                            "gte": lookup_query.get('{}_from'.format(cannabinoid), 0),
                            "lte": lookup_query.get('{}_to'.format(cannabinoid), 100),
                        }
                    }
                })

        location = current_user.get_location()
        proximity = current_user.proximity
        sort_query = []
        for item in list(lookup_query.get('sort', [])) + [
            VtSearchSerializer.BEST_MATCH, VtSearchSerializer.NAME, VtSearchSerializer.LOCATION,
            VtSearchSerializer.PRICE, VtSearchSerializer.MAX_PRICE_GRAM, VtSearchSerializer.PRICE_EIGHTH,
            VtSearchSerializer.MAX_PRICE_EIGHTH, VtSearchSerializer.PRICE_QUARTER,
            VtSearchSerializer.MAX_PRICE_QUARTER
        ]:
            sort_query.append(
                VtSearchSerializer.SORT_FIELDS[item](
                    lat=location and location.lat or 0, lon=location and location.lng or 0,
                    proximity=proximity)
            )

        query = {
            "from": start_from,
            "size": size,
            'sort': sort_query,
            "query": {
                "function_score": {
                    "query": {
                        "bool": {
                            "must": must_query,
                            "must_not": {
                                "exists": {"field": "removed_date"}
                            }
                        }
                    },
                    "functions": [{
                        "script_score": {
                            "script": {
                                "lang": "painless",
                                "params": lookup_query,
                                "inline": ADVANCED_SEARCH_SCORE
                            }
                        }
                    }]
                }
            }
        }
        es_response = self._request(method, url, data=json.dumps(query, cls=PythonJSONEncoder))
        return self._transform_search_results(es_response)

    def _transform_search_results(self, es_response):
        vts = es_response.get('hits', {}).get('hits', [])
        total = es_response.get('hits', {}).get('total', 0)
        processed_results = []

        for s in vts:
            source = s.get('_source', {})
            sort = s.get('sort', [None] * 7)[-7:]
            distance, gram, max_gram, eighth, max_eighth, quarter, max_quarter = sort

            vt_image = VtImage.objects.filter(vt=source.get('id'), is_approved=True)\
                .exclude(Q(image__isnull=True) | Q(image='')).first()
            processed_results.append({
                'id': source.get('id'),
                'name': source.get('name'),
                'vt_slug': source.get('vt_slug'),
                'variety': source.get('variety'),
                'category': source.get('category'),
                'image_url': vt_image.image.url if vt_image and vt_image.image else None,
                'cup_winner': source.get('cup_winner'),
                'cannabinoids': source.get('cannabinoids'),
                'terpenes': source.get('terpenes'),
                'distance': distance,
                'price_gram': gram if isinstance(gram, float) else None,
                'max_price_gram': max_gram if isinstance(max_gram, float) else None,
                'price_eighth': eighth if isinstance(eighth, float) else None,
                'max_price_eighth': max_eighth if isinstance(max_eighth, float) else None,
                'price_quarter': quarter if isinstance(quarter, float) else None,
                'max_price_quarter': max_quarter if isinstance(max_quarter, float) else None
            })
        return {
            'list': processed_results,
            'total': total
        }

    def lookup_business_location(self, query, bus_type=None, location=None, timezone=None):
        if bus_type is None:
            bus_type = []

        method = self.METHODS.get('POST')
        url = '{base}{index}/_search'.format(
            base=self.BASE_ELASTIC_URL,
            index=self.URLS.get('BUSINESS_LOCATION'),
        )

        # context suggester: https://www.elastic.co/guide/en/elasticsearch/reference/current/suggester-context.html
        contexts = {
            "bus_type": bus_type
        }

        query = {
            "_source": {
                "excludes": ["menu_items", "phone", "ext", "removed_by_id", "created_date", "manager_name",
                             "location_email", "location_raw", "location_name_suggest"]
            },
            "suggest": {
                "location_suggestion": {
                    "text": query,
                    "completion": {
                        "field": "location_name_suggest",
                        "size": 25,
                        "contexts": contexts
                    }
                }
            }
        }

        if location:
            # add user location if we have one
            query['suggest']['location_suggestion']['completion']['contexts']['location'] = location

            # inline script here gets distance from each dispensary and converts to km then to miles
            query['script_fields'] = {
                "distance": {
                    "script": {
                        "lang": "painless",
                        "inline": "return doc['location'].planeDistance({lat}, {lon}) * 0.001 * 0.6213712".format(**location)
                    }
                }
            }

        es_response = self._request(method, url, data=json.dumps(query))
        results = self._transform_dispensary_suggest_results(es_response)
        return results

    def _transform_dispensary_suggest_results(self, es_response):
        suggests = es_response.get('suggest', {}).get('location_suggestion', [])
        total = 0
        payloads = []
        has_location = False

        if len(suggests) > 0:
            suggestion = suggests[0]
            total = len(suggestion.get('options'))
            for option in suggestion.get('options'):
                biz_location = option.get('_source')
                if not biz_location:
                    continue
                biz_location['distance'] = option.get('fields', {}).get('distance', [])[0] if option.get('fields', {}).get('distance') else None
                biz_location['image'] = biz_location['image'] if biz_location['image'] else None
                biz_location['open'] = get_open_closed(biz_location) in ['Opened', 'Closing Soon']

                # sort by location only if all locations are present
                if biz_location['distance'] is not None:
                    has_location = True
                else:
                    has_location = False

                payloads.append(biz_location)

            # ES suggest searches don't like to sort by anything other than suggestion weight
            # so sort in python here so closest is always first. Maybe this will change in the future
            # see https://www.elastic.co/guide/en/elasticsearch/reference/5.6/suggester-context.html#_geo_location_query
            if has_location:
                payloads.sort(key=lambda x: x.get('distance'))

        return {
            'total': total,
            'payloads': payloads
        }

    def _transform_query_results(self, es_response):
        hits = es_response.get('hits', {})
        total = hits.get('total', 0)
        payloads = []

        for h in hits.get('hits', []):
            vt = h.get('_source')
            if not vt.get('removed_date'):
                payloads.append(vt)

        return {
            'total': total,
            'payloads': payloads
        }

    def _transform_suggest_results(self, es_response, include_locations=False, include_image=False, current_user=None):
        suggests = es_response.get('suggest', {}).get('name_suggestion', [])
        total = 0
        payloads = []

        if len(suggests) > 0:
            suggestion = suggests[0]
            total = len(suggestion.get('options'))
            for option in suggestion.get('options'):
                vt = option.get('_source')
                if vt and not vt.get('removed_date'):

                    if include_locations and current_user:
                        dispensaries = self.get_locations(
                            vt.get('id'), "dispensary", current_user, only_active=True)
                        dispensaries = self.transform_location_results(dispensaries, vt.get('id'))

                        deliveries = self.get_locations(
                            vt.get('id'), "delivery", current_user, only_active=True)
                        deliveries = self.transform_location_results(deliveries, vt.get('id'))
                    else:
                        dispensaries = []
                        deliveries = []

                    if include_image:
                        vt_image = VtImage.objects.filter(vt=vt.get('id'), is_approved=True).first()
                        vt['image_url'] = vt_image.image.url if vt_image and vt_image.image else None

                    vt['deliveries'] = deliveries
                    vt['locations'] = dispensaries
                    payloads.append(vt)
        return {
            'total': total,
            'payloads': payloads
        }
