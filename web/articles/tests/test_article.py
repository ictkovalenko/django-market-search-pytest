from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from web.articles.tests.factories import ArticleFactory, CategoryFactory
from web.system.models import PermanentlyRemoved


class ArticleTestCase(APITestCase):

    def setUp(self):
        self.category = CategoryFactory()
        self.article = ArticleFactory(category=self.category)
        self.url = reverse('view_article', args=(self.category.slug, self.article.slug))

    def test_get_article(self):
        """
        Get article by slug
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, self.article.title)

        self.article.slug = 'test'
        self.article.save()
        self.url = reverse('view_article', args=(self.category.slug, self.article.slug))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, self.article.title)

    def test_remove_permanently(self):
        """
        Check after article was removed it was added to PermanentlyRemoved with 410 code
        """
        self.article.delete()
        self.assertEqual(PermanentlyRemoved.objects.count(), 1)
        item = PermanentlyRemoved.objects.first()
        self.assertEqual(item.status, status.HTTP_410_GONE)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_410_GONE)

    def test_redirect_permanently(self):
        """
        Check after article was changed it was added to PermanentlyRemoved with 301 code
        """
        self.article.slug = 'test'
        self.article.save()

        self.assertEqual(PermanentlyRemoved.objects.count(), 1)
        item = PermanentlyRemoved.objects.first()
        self.assertEqual(item.status, status.HTTP_301_MOVED_PERMANENTLY)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)

    def test_redirect_permanently_when_category_changes(self):
        """
        Check after article category was changed it was added to PermanentlyRemoved with 301 code
        """
        self.article.category = CategoryFactory()
        self.article.save()

        self.assertEqual(PermanentlyRemoved.objects.count(), 1)
        item = PermanentlyRemoved.objects.first()
        self.assertEqual(item.status, status.HTTP_301_MOVED_PERMANENTLY)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)

    def test_change_category(self):
        """
        Check after category was changed it was added to PermanentlyRemoved with 301 code
        """
        self.category.slug = 'test'
        self.category.save()

        self.assertEqual(PermanentlyRemoved.objects.count(), 1)
        item = PermanentlyRemoved.objects.first()
        self.assertEqual(item.status, status.HTTP_301_MOVED_PERMANENTLY)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)

    def test_change_subcategory(self):
        """
        Check after category was changed it was added to PermanentlyRemoved with 301 code
        """
        self.category.parent = CategoryFactory()
        self.category.save()

        self.assertEqual(PermanentlyRemoved.objects.count(), 1)
        item = PermanentlyRemoved.objects.first()
        self.assertEqual(item.status, status.HTTP_301_MOVED_PERMANENTLY)
        self.assertEqual(item.url, '/{}/{}/'.format(self.category.slug, self.article.slug))
        self.assertEqual(item.redirect_url, '/{}/{}/{}/'.format(self.category.parent.slug,
                                                                self.category.slug, self.article.slug))

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)

        # Add parent category
        self.category.parent.parent = CategoryFactory()
        self.category.parent.save()

        self.assertEqual(PermanentlyRemoved.objects.count(), 2)
        item = PermanentlyRemoved.objects.first()
        self.assertEqual(item.url, '/{}/{}/{}/'.format(
            self.category.parent.slug, self.category.slug, self.article.slug))

        # Update Slug in the parent category
        old_slug = self.category.parent.parent.slug
        self.category.parent.parent.slug = 'test'
        self.category.parent.parent.save()
        self.assertEqual(PermanentlyRemoved.objects.count(), 3)
        item = PermanentlyRemoved.objects.first()
        self.assertEqual(item.url, '/{}/{}/{}/{}/'.format(
            old_slug, self.category.parent.slug, self.category.slug, self.article.slug))

    def test_view_page_url(self):
        self.article = ArticleFactory()
        self.url = reverse('view_page', args=(self.article.slug,))
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.article.category = CategoryFactory()
        self.article.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)
