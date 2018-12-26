from __future__ import unicode_literals, absolute_import

from django.core.urlresolvers import reverse
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from rest_framework import status

from web.articles.models import Article, Category
from web.system.models import PermanentlyRemoved


@receiver(post_delete, sender=Article)
def remove_permanently(sender, instance, **kwargs):
    """
    Add record to PermanentlyRemoved model
    """
    PermanentlyRemoved.objects.create(
        status=status.HTTP_410_GONE,
        url=instance.get_absolute_url()
    )


@receiver(post_save, sender=Article)
def moved_permanently(sender, instance, raw, created, **kwargs):
    """
    Add record to PermanentlyRemoved model with 301 status code
    """
    if created:
        return

    data = {
        'slug': instance.slug,
        'category_slug': instance.category.slug if instance.category else None
    }

    if instance.original_data != data:
        if instance.original_data['category_slug']:
            url = reverse('view_article', kwargs={
                'category_slug': instance.original_data['category_slug'],
                'article_slug': instance.original_data['slug']})
        else:
            url = reverse('view_page', args=(instance.original_data['slug'],))

        PermanentlyRemoved.objects.create(
            status=status.HTTP_301_MOVED_PERMANENTLY,
            url=url,
            redirect_url=instance.get_absolute_url()
        )
        instance.original_data = data


@receiver(post_save, sender=Category)
def category_moved_permanently(sender, instance, raw, created, **kwargs):
    """
    Add record to PermanentlyRemoved model with 301 status code
    """

    def permanently_redirect(category):
        """
        Recursively add redirect for each articles per category
        """
        for article in category.articles.all():
            redirect_url = article.get_absolute_url()

            url = redirect_url.replace('/{}/'.format(instance.slug), '/{}/'.format(instance.original_data['slug']))
            if not instance.original_data['parent'] and original_data['parent']:
                url = url.replace('/{}/'.format(original_data['parent']), '/')

            PermanentlyRemoved.objects.create(
                status=status.HTTP_301_MOVED_PERMANENTLY,
                url=url,
                redirect_url=redirect_url
            )

        for subcategory in category.subcategories.all():
            permanently_redirect(subcategory)

    if created:
        return

    original_data = {'slug': instance.slug, 'parent': instance.parent}
    if instance.original_data['slug'] and instance.original_data != original_data:

        # Add redirect for articles for current category
        permanently_redirect(instance)
        instance.original_data = original_data
