from datetime import datetime

from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse

from web.search.models import Vt


class VtSitemap(Sitemap):
    changefreq = 'weekly'
    protocol = 'https'

    def items(self):
        return Vt.objects.filter(removed_date=None)

    def lastmod(self, obj):
        return datetime.now()


class StaticViewSitemap(Sitemap):
    changefreq = 'monthly'
    protocol = 'https'

    def items(self):
        return ['home', 'about']

    def location(self, item):
        return reverse(item)

    def lastmod(self, obj):
        return datetime.now()
