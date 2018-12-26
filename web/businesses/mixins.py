import pytz
from django.db.models import Q
from django.shortcuts import get_object_or_404

from web.businesses.models import Business, BusinessLocation


class BusinessDetailMixin(object):

    def get_object(self):
        return get_object_or_404(Business, pk=self.kwargs.get('business_id'), users=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(BusinessDetailMixin, self).get_context_data(**kwargs)
        business = self.get_object()
        locations = BusinessLocation.objects.filter(business=business, removed_date=None).order_by('id')
        context['locations'] = locations
        context['dispensaries'] = locations.filter(Q(dispensary=True) | Q(delivery=True))
        context['first_location'] = locations.first()
        context['grow_houses'] = locations.filter(grow_house=True)
        context['timezones'] = pytz.common_timezones
        context['business'] = business
        return context
