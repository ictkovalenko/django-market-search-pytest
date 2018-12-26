# -*- coding: utf-8 -*-
import json
import logging

from django.core.management.base import BaseCommand, CommandError

from web.search import es_mappings
from web.search.es_mappings import vt_rating_mapping
from web.search.es_service import SearchElasticService as ElasticService
from web.search.models import VtRating

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """
            Setup an index to store user reviews for a vts
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
        self.create_index()

    def create_index(self):
        if self.DROP_AND_REBUILD:
            self.drop_and_rebuild()

        self.load_user_vts_reviews()

    def drop_and_rebuild(self):
        es = ElasticService()

        # create custom analyzer for vt names
        index_settings = {
            "mappings": {
                es_mappings.TYPES.get('vt_rating'): vt_rating_mapping
            }
        }

        # delete index
        es.delete_index(self.INDEX)

        # set analyzer
        es.set_settings(self.INDEX, index_settings)

        self.stdout.write('1. Setup complete for [{0}] index'.format(self.INDEX))

    def load_user_vts_reviews(self):
        es = ElasticService()
        user_ratings = VtRating.objects.all()

        bulk_data = []

        # build up bulk update
        for ur in user_ratings:
            action_data = json.dumps({
                'index': {}
            })
            bulk_data.append(action_data)
            bulk_data.append(json.dumps({
                'id': ur.id,
                'vt_id': ur.vt.id,
                'user_id': ur.created_by.id,
                'effects': ur.effects,
                'effects_changed': ur.effects_changed,
                'benefits': ur.benefits,
                'benefits_changed': ur.benefits_changed,
                'side_effects': ur.side_effects,
                'side_effects_changed': ur.side_effects_changed,
                'status': ur.status,
                'removed_date': ur.removed_date.isoformat() if ur.removed_date else None
            }))

        if len(bulk_data) == 0:
            self.stdout.write('   ---> Nothing to update')
            return

        transformed_bulk_data = '{0}\n'.format('\n'.join(bulk_data))
        results = es.bulk_index(transformed_bulk_data, index=self.INDEX,
                                index_type=es_mappings.TYPES.get('vt_rating'))

        if results.get('success') is False:
            # keep track of any errors we get
            logger.error(('Error updating {index}/{index_type} in ES. Errors: {errors}'.format(
                index=self.INDEX, index_type=es_mappings.TYPES.get('vt'), errors=results.get('errors')
            )))

        self.stdout.write('2. Updated [{0}] index with {1} user reviews'.format(self.INDEX, len(user_ratings)))
