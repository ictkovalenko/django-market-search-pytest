from __future__ import unicode_literals, absolute_import

from django.core.urlresolvers import reverse
from django.db.models.signals import post_save, pre_save, post_delete, pre_delete
from django.dispatch import receiver
from rest_framework import status

from web.businesses.emails import EmailService
from web.businesses.es_service import BusinessLocationESService
from web.businesses.models import BusinessLocation, State, City, BusinessLocationMenuItem, \
    BusinessLocationMenuUpdate, BusinessLocationMenuUpdateRequest, Payment, Business
from web.search.models import Vt
from web.search.vt_es_service import VtESService
from web.system.models import PermanentlyRemoved


@receiver(pre_save, sender=BusinessLocation)
def pre_save_business_location(sender, **kwargs):
    business_location = kwargs.get('instance')
    save_city_and_state(business_location)


@receiver(post_save, sender=BusinessLocation)
def post_save_business_location(sender, **kwargs):
    business_location = kwargs.get('instance')
    BusinessLocationESService().save_business_location(business_location)
    original_location = {field: getattr(business_location, field) for field in business_location.VT_INDEX_FIELDS}

    if business_location.original_location != original_location:
        # Update vt
        vts = Vt.objects.filter(menu_items__business_location=business_location)
        for vt in vts:
            VtESService().save_vt(vt)
        business_location.original_location = original_location


def save_city_and_state(business_location):
    state = business_location.state
    city = business_location.city

    if state and not State.objects.filter(abbreviation__iexact=state.lower()).exists():
        s = State(abbreviation=state.upper())
        s.save()
    else:
        s = State.objects.get(abbreviation__iexact=state.lower())

    if city and not City.objects.filter(state=s, full_name__iexact=city.lower()).exists():
        c = City(state=s, full_name=city)
        c.save()
    else:
        c = City.objects.get(state=s, full_name__iexact=city.lower())

    business_location.state_fk = s
    business_location.city_fk = c


@receiver(post_save, sender=BusinessLocationMenuItem)
def save_es_menu_item(sender, **kwargs):
    menu_item = kwargs.get('instance')

    BusinessLocationESService().save_menu_item(menu_item)
    # Update Vt
    VtESService().save_vt(menu_item.vt)
    BusinessLocationMenuUpdate.record_business_location_menu_update(menu_item.business_location)

    unserved_requests = BusinessLocationMenuUpdateRequest.objects.filter(
        business_location=menu_item.business_location,
        served=False,
    )
    unserved_requests = unserved_requests.select_related('user', 'business_location')

    email_service = EmailService()
    for request in unserved_requests:
        if request.send_notification:
            email_service.send_menu_update_request_served_email(request)

        request.served = True
        request.save()


def update_business_payments(business_id):
    amount, date = None, None

    last_payment = Payment.objects.filter(business_id=business_id).order_by('date').last()

    if last_payment is not None:
        amount = last_payment.amount
        date = last_payment.date

    Business.objects.filter(id=business_id).update(last_payment_amount=amount,
                                                   last_payment_date=date)


@receiver(post_save, sender=Payment)
def post_save_payment(sender, **kwargs):
    payment = kwargs.get('instance')
    update_business_payments(payment.business_id)


@receiver(post_delete, sender=Payment)
def post_delete_payment(sender, **kwargs):
    payment = kwargs.get('instance')
    update_business_payments(payment.business_id)


@receiver(post_delete, sender=BusinessLocationMenuItem)
def post_delete_menu_item(sender, instance, **kwargs):
    """
    Delete menu item from ES index
    """
    BusinessLocationESService().delete_menu_item(instance)
    # Update Vt
    VtESService().save_vt(instance.vt)


@receiver(pre_delete, sender=Business)
def remove_permanently(sender, instance, **kwargs):
    """
    Add record to PermanentlyRemoved model for each location
    Update ES index
    """
    for location in BusinessLocation.objects.filter(business_id=instance.id):
        BusinessLocationESService().delete_business_location(location.id)

        PermanentlyRemoved.objects.create(
            status=status.HTTP_410_GONE,
            url=reverse('businesses:dispensary_info',
                        args=(location.state, location.city_slug, location.slug_name))
        )


@receiver(post_delete, sender=BusinessLocation)
def remove_business_location_permanently(sender, instance, **kwargs):
    """
    Add record to PermanentlyRemoved model for the location
    Update ES index
    """
    BusinessLocationESService().delete_business_location(instance.id)

    PermanentlyRemoved.objects.create(
        status=status.HTTP_410_GONE,
        url=reverse('businesses:dispensary_info',
                    args=(instance.state, instance.city_slug, instance.slug_name))
    )
