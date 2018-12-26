# -*- coding: utf-8 -*-
import csv
import logging


from django.core.management.base import BaseCommand, CommandError

from web.users.models import User

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """
            Export data from csv
        """

    def add_arguments(self, parser):
        parser.add_argument('--csv_path',
                            action='store',
                            default=None,
                            dest='csv_path',
                            help='Absolute path to save export file.')

    def handle(self, *args, **options):
        if options.get('csv_path'):
            csv_path = options.get('csv_path')
        else:
            raise CommandError('csv_path is required')

        with open(csv_path, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['First Name', 'Last Name', 'Email', 'Type', 'Email Verified', 'Date Joined'])
            n = User.objects.count()

            self.stdout.write('Exporting {n} users to {csv_path}'.format(n=n, csv_path=csv_path))
            for user in User.objects.iterator():
                writer.writerow([user.first_name, user.last_name, user.email,
                                 user.type, user.is_email_verified, user.date_joined])

            self.stdout.write('DONE')
