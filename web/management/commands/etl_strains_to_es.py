# -*- coding: utf-8 -*-
import json
import logging
import time

from django.core.management.base import BaseCommand, CommandError

from web.search import es_mappings
from web.search.es_mappings import vt_mapping, vt_review_mapping
from web.search.es_service import SearchElasticService as ElasticService
from web.search.models import Vt, VtReview
from web.search.serializers import VtESSerializer
from web.search.vt_es_service import VtESService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """
            ETL vt data from psql to ES
        """

    def add_arguments(self, parser):
        parser.add_argument('--drop_and_rebuild',
                            action='store_true',
                            dest='drop_and_rebuild',
                            help='If arg is included will drop given index, set mappings, analyzers')

        parser.add_argument('--index',
                            action='store',
                            default=None,
                            dest='index',
                            help='Name of ES index to store results in')

    def handle(self, *args, **options):
        if options.get('index'):
            self.INDEX = options.get('index').lower()
        else:
            raise CommandError('Index is required')

        self.DROP_AND_REBUILD = options.get('drop_and_rebuild', False)
        self.etl_vts()

    def etl_vts(self):
        if self.DROP_AND_REBUILD:
            self.drop_and_rebuild()

        self.load_vts()
        time.sleep(2)
        self.load_vt_reviews()

    def drop_and_rebuild(self):
        es = ElasticService()

        # create custom analyzer for vt names
        index_settings = {
            "settings": {
                "analysis": {
                    "tokenizer": {
                        "exact_tokenizer": {
                            "type": "pattern",
                            "pattern": "\\*"
                        }
                    },
                    "filter": {
                        "replace_special_chars": {
                          "type": "pattern_replace",
                          "pattern": "[ :\\-+=\\&\\|\\>\\<\\!\\(\\)\\{\\}\\[\\]\\^\\\\\"\\~\\*\\?\\;\\/\\.\\,\\_]",
                          "replacement": ""
                        }
                    },
                    "analyzer": {
                        "name_analyzer": {
                            "type": "custom",
                            "tokenizer": "whitespace",
                            "filter": ["lowercase"]
                        },
                        "exact_name_analyzer": {
                            "type": "custom",
                            "tokenizer": "exact_tokenizer",
                            "filter": [
                                "lowercase",
                                "replace_special_chars"
                            ]
                        }
                    }
                }
            },
            "mappings": {
                es_mappings.TYPES.get('vt'): vt_mapping,
                es_mappings.TYPES.get('vt_review'): vt_review_mapping
            }
        }

        # delete index
        es.delete_index(self.INDEX)

        # set analyzer
        es.set_settings(self.INDEX, index_settings)

        self.stdout.write('1. Setup complete for [{0}] index'.format(self.INDEX))

    def load_vts(self):
        es = ElasticService()
        # fetch all vts
        vts = Vt.objects.all().prefetch_related('menu_items')

        bulk_vt_data = []

        # build up bulk update
        for s in vts:
            action_data = json.dumps({
                'index': {}
            })

            bulk_vt_data.append(action_data)

            es_serializer = VtESSerializer(instance=s)
            bulk_vt_data.append(json.dumps(es_serializer.data))

        if len(bulk_vt_data) == 0:
            self.stdout.write('   ---> Nothing to update')
            return

        transformed_bulk_data = '{0}\n'.format('\n'.join(bulk_vt_data))
        results = es.bulk_index(transformed_bulk_data, index=self.INDEX, index_type=es_mappings.TYPES.get('vt'))

        if results.get('success') is False:
            # keep track of any errors we get
            logger.error(('Error updating {index}/{index_type} in ES. Errors: {errors}'.format(
                index=self.INDEX,
                index_type=es_mappings.TYPES.get('vt'),
                errors=results.get('errors')
            )))

        self.stdout.write(
            '2. Updated [{0}] index with {1} vts'.format(self.INDEX, len(vts))
        )

    def load_vt_reviews(self):
        self.stdout.write('3. Updating a vt reviews')

        es = ElasticService()
        reviews = VtReview.objects.all()
        bulk_reviews_data = []
        vts_cache_map = {}

        for r in reviews:
            vt_id = r.vt.id
            vt = vts_cache_map.get(vt_id)

            if vt is None or len(vt) == 0:
                es_vt = VtESService().get_vt_by_db_id(vt_id)
                vt = es_vt.get('hits', {}).get('hits', [])
                vts_cache_map[vt_id] = vt

            if vt is None or len(vt) == 0:
                raise CommandError('   !!!---> No vt found in ES for id [{0}].'.format(vt_id))

            action_data = json.dumps({
                'index': {
                    '_parent': vt[0].get('_id')
                }
            })

            bulk_reviews_data.append(action_data)
            bulk_reviews_data.append(json.dumps({
                'id': r.id,
                'rating': r.rating,
                'review': r.review,
                'review_approved': r.review_approved,
                'created_date': r.created_date.isoformat(),
                'created_by': r.created_by.id,
                'last_modified_date': r.last_modified_date.isoformat() if r.last_modified_date else None,
                'last_modified_by': r.last_modified_by.id if r.last_modified_by else None
            }))

        if len(bulk_reviews_data) == 0:
            self.stdout.write('   ---> No reviews to update')
            return

        transformed_bulk_data = '{0}\n'.format('\n'.join(bulk_reviews_data))
        results = es.bulk_index(transformed_bulk_data, index=self.INDEX,
                                index_type=es_mappings.TYPES.get('vt_review'))

        if results.get('success') is False:
            # keep track of any errors we get
            logger.error(('Error updating {index}/{index_type} in ES. Errors: {errors}'.format(
                index=self.INDEX,
                index_type=es_mappings.TYPES.get('vt_review'),
                errors=results.get('errors')
            )))

        self.stdout.write(
            'Updated [{0}] index with {1} vt reviews'.format(self.INDEX, len(reviews))
        )
