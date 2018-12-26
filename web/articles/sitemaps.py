from django.contrib.sitemaps import Sitemap

from web.articles.models import Article


class ArticleSitemap(Sitemap):
    changefreq = 'monthly'
    protocol = 'https'

    def items(self):
        return Article.objects.all()

    def lastmod(self, obj):
        return obj.created_date
