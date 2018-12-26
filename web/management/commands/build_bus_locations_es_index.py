# -*- coding: utf-8 -*-
import json
import logging

from django.core.management.base import BaseCommand, CommandError

from web.businesses.models import BusinessLocation, BusinessLocationMenuItem
from web.businesses.es_service import BusinessLocationESService
from web.search import es_mappings
from web.search.es_mappings import business_location_mapping
from web.search.es_service import SearchElasticService as ElasticService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """
            Setup an index to store business locations and the menu items
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

        self.load_business_locations()

    def drop_and_rebuild(self):
        es = ElasticService()

        # create custom analyzer for vt names
        index_settings = {
            "settings": {
                "analysis": {
                    "analyzer": {
                        "name_analyzer": {
                            "type": "custom",
                            "tokenizer": "whitespace",
                            "filter": ["lowercase"]
                        }
                    }
                }
            },
            "mappings": {
                es_mappings.TYPES.get('business_location'): business_location_mapping
            }
        }

        # delete index
        es.delete_index(self.INDEX)

        # set analyzer
        es.set_settings(self.INDEX, index_settings)

        self.stdout.write('1. Setup complete for [{0}] index'.format(self.INDEX))

    def load_business_locations(self):
        es = ElasticService()
        bes = BusinessLocationESService()
        locations = BusinessLocation.objects.all()
        locations_data = []

        for l in locations:
            menu_items_raw = BusinessLocationMenuItem.objects.filter(business_location=l)
            menu_items = []

            for mi in menu_items_raw:
                vt = mi.vt
                menu_items.append({
                    "id": mi.pk,
                    "vt_id": vt.pk,
                    "vt_name": vt.name,
                    "price_gram": mi.price_gram,
                    "price_eighth": mi.price_eighth,
                    "price_quarter": mi.price_quarter,
                    "price_half": mi.price_half,
                    "in_stock": mi.in_stock,
                    "removed_date": mi.removed_date.isoformat() if mi.removed_date else None
                })

            action_data = json.dumps({
                'index': {}
            })
            locations_data.append(action_data)
            location_data = {
                "business_id": l.business.pk,
                "business_location_id": l.pk,
                "category": l.category,
                "slug_name": l.slug_name,
                "location_name": l.location_name,
                "manager_name": l.manager_name,
                "location_email": l.location_email,
                "dispensary": l.dispensary,
                "delivery": l.delivery,
                "grow_house": l.grow_house,
                "delivery_radius": l.delivery_radius,
                "street1": l.street1,
                "city": l.city,
                "state": l.state,
                "zip_code": l.zip_code,
                "phone": l.phone,
                "ext": l.ext,
                "timezone": l.timezone,
                "removed_by_id": l.removed_by,
                "removed_date": l.removed_date.isoformat() if l.removed_date else None,
                "created_date": l.created_date.isoformat() if l.created_date else None,
                "mon_open": l.mon_open.isoformat() if l.mon_open else None,
                "mon_close": l.mon_close.isoformat() if l.mon_close else None,
                "tue_open": l.tue_open.isoformat() if l.tue_open else None,
                "tue_close": l.tue_close.isoformat() if l.tue_close else None,
                "wed_open": l.wed_open.isoformat() if l.wed_open else None,
                "wed_close": l.wed_close.isoformat() if l.wed_close else None,
                "thu_open": l.thu_open.isoformat() if l.thu_open else None,
                "thu_close": l.thu_close.isoformat() if l.thu_close else None,
                "fri_open": l.fri_open.isoformat() if l.fri_open else None,
                "fri_close": l.fri_close.isoformat() if l.fri_close else None,
                "sat_open": l.sat_open.isoformat() if l.sat_open else None,
                "sat_close": l.sat_close.isoformat() if l.sat_close else None,
                "sun_open": l.sun_open.isoformat() if l.sun_open else None,
                "sun_close": l.sun_close.isoformat() if l.sun_close else None,
                "menu_items": menu_items,
                "image": l.image_url,
                "url": l.url,
                "urls": l.urls,
                "location_name_suggest": bes.generate_autocomplete_data(l)
            }

            if l.lat and l.lng:
                location_data["location"] = {"lat": l.lat, "lon": l.lng}
                location_data["location_raw"] = l.location_raw
            else:
                location_data["location"] = None
                location_data["location_raw"] = ""

            locations_data.append(json.dumps(location_data))

        if len(locations_data) == 0:
            self.stdout.write('   ---> Nothing to update')
            return

        transformed_bulk_data = '{0}\n'.format('\n'.join(locations_data))
        results = es.bulk_index(transformed_bulk_data, index=self.INDEX,
                                index_type=es_mappings.TYPES.get('business_location'))

        if results.get('success') is False:
            # keep track of any errors we get
            logger.error(('Error updating {index}/{index_type} in ES. Errors: {errors}'.format(
                index=self.INDEX, index_type=es_mappings.TYPES.get('business_location'), errors=results.get('errors')
            )))

        self.stdout.write('2. Updated [{0}] index with {1} business locations'.format(self.INDEX, len(locations)))
