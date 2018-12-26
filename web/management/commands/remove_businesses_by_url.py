# -*- coding: utf-8 -*-
import csv
import logging

from django.core.management.base import BaseCommand, CommandError

from web.businesses.models import BusinessLocation


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """
            Permanently remove businesses identified by the urls in the *.csv file.
        """

    def add_arguments(self, parser):
        parser.add_argument('--csv_path',
                            action='store',
                            default=None,
                            dest='csv_path',
                            help='Path to csv relative to current directory')

    def handle(self, *args, **options):
        csv_path = options.get('csv_path')

        if csv_path is None:
            raise CommandError('csv_path is required')

        with open(csv_path) as f:
            reader = csv.reader(f)

            for i, row in enumerate(reader):
                url = row[0]

                state, city_slug, slug_name, _ = url.split('/')[-4:]

                kwargs = {
                    'state__iexact': state,
                    'city_slug__iexact': city_slug,
                    'slug_name__iexact': slug_name,
                }

                print(i + 1, url)

                try:
                    location = BusinessLocation.objects.get(**kwargs)
                    location.business.delete()
                    print('Removed successfully')
                    print('')

                except BusinessLocation.DoesNotExist:
                    print('Not found')
                    print('')
