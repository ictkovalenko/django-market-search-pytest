from __future__ import unicode_literals, absolute_import

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from rest_framework import status

from web.search.models import VtReview, Vt, VtRating
from web.search.serializers import VtReviewESSerializer
from web.search.vt_es_service import VtESService
from web.system.models import PermanentlyRemoved
from web.users.models import User


@receiver(post_save, sender=VtReview)
def create_es_review(sender, **kwargs):
    vt_review = kwargs.get('instance')
    es_serializer = VtReviewESSerializer(vt_review)
    data = es_serializer.data
    data['created_by'] = vt_review.created_by.id
    data['last_modified_by'] = vt_review.last_modified_by.id if vt_review.last_modified_by else None
    VtESService().save_vt_review(data, vt_review.id, vt_review.vt.id)


@receiver(post_save, sender=Vt)
def create_es_vt(sender, **kwargs):
    vt = kwargs.get('instance')
    VtESService().save_vt(vt)

    if User.objects.filter(email='tech+mod+rate_bot@').exists():
        rate_bot = User.objects.get(email='tech+mod+rate_bot@')
        if not VtRating.objects.filter(vt=vt, created_by=rate_bot, removed_date=None).exists():
            r = VtRating(vt=vt, created_by=rate_bot, effects=vt.effects, benefits=vt.benefits,
                             side_effects=vt.side_effects, status='pending')
            r.save()


@receiver(pre_delete, sender=Vt)
def remove_permanently(sender, instance, **kwargs):
    """
    Add record to PermanentlyRemoved model
    Update ES index
    """
    VtESService().delete_vt(instance.pk)
    PermanentlyRemoved.objects.create(
        status=status.HTTP_410_GONE,
        url=instance.get_absolute_url()
    )
