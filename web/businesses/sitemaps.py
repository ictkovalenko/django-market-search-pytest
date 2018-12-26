from datetime import datetime

from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse

from web.businesses.models import BusinessLocation, State, City


class BusinessLocationSitemap(Sitemap):
    changefreq = 'daily'
    protocol = 'https'

    def items(self):
        return BusinessLocation.objects.filter(removed_date=None).select_related('state_fk', 'city_fk')

    def lastmod(self, obj):
        return datetime.now()


class StateRootSitemap(Sitemap):
    changefreq = 'daily'
    protocol = 'https'

    def items(self):
        return State.objects.all()

    def lastmod(self, obj):
        return datetime.now()


class CityRootSitemap(Sitemap):
    changefreq = 'daily'
    protocol = 'https'

    def items(self):
        return City.objects.all()

    def lastmod(self, obj):
        return datetime.now()


class DispensariesRootSitemap(Sitemap):
    changefreq = 'daily'
    protocol = 'https'

    def items(self):
        return ['businesses:dispensaries_list']

    def location(self, item):
        return reverse(item)

    def lastmod(self, obj):
        return datetime.now()
