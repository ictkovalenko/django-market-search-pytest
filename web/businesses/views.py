# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import urllib.parse
from datetime import datetime

from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import RedirectView, TemplateView, FormView, DetailView

from web.analytics.models import Event
from web.analytics.service import Analytics
from web.businesses.api.services import FeaturedBusinessLocationService
from web.businesses.emails import EmailService
from web.businesses.forms import ClaimForm, AnalyticsFilterForm
from web.businesses.mixins import BusinessDetailMixin
from web.businesses.models import Business, BusinessLocation, ReportOutOfStock
from web.businesses.models import State, City, BusinessLocationMenuUpdateRequest
from web.businesses.utils import NamePaginator
from web.search.services import get_vts_and_images_for_location
from web.users.models import User


class BusinessSignUpWizardView(TemplateView):
    template_name = 'pages/signup/b2b/wizard.html'


class BusinessSignUpDoneView(TemplateView):
    template_name = 'pages/signup/b2b/almost_done.html'


class ConfirmEmailView(TemplateView):
    template_name = 'pages/signup/b2b/email_confirmed.html'

    def get_context_data(self, **kwargs):
        uid = kwargs.get('uid')
        user = User.objects.get(pk=uid)
        user.is_email_verified = True
        user.save()
        business = Business.objects.get(created_by=user)
        business.trial_period_start_date = datetime.now()
        business.save()

        context = super(ConfirmEmailView, self).get_context_data(**kwargs)
        context['business'] = business
        return context


class ConfirmMenuView(TemplateView):
    template_name = 'pages/business/menu_date_update.html'

    def get(self, request, *args, **kwargs):
        secret_key = kwargs.get('secret_key')
        try:
            update_request = BusinessLocationMenuUpdateRequest.objects.get(secret_key=secret_key)
        except BusinessLocationMenuUpdateRequest.DoesNotExist:
            raise Http404

        location = update_request.business_location
        current_datetime = location.get_current_datetime()

        to_update = BusinessLocation.objects.filter(id=location.id, menu_updated_date__lt=current_datetime)
        to_update.update(menu_updated_date=current_datetime.date())

        unserved_requests = BusinessLocationMenuUpdateRequest.objects.filter(
            business_location=location,
            served=False,
        )
        unserved_requests = unserved_requests.select_related('user', 'business_location')

        email_service = EmailService()
        for request in unserved_requests:
            if request.send_notification:
                email_service.send_menu_update_request_served_email(request)

            request.served = True
            request.save()

        return super().get(request, *args, **kwargs)


class BusinessDetailView(BusinessDetailMixin, TemplateView):
    template_name = 'pages/business/business_detail.html'

    def get_context_data(self, **kwargs):
        context = super(BusinessDetailView, self).get_context_data(**kwargs)
        context['tab'] = 'info'
        return context


class BusinessMenuView(BusinessDetailMixin, TemplateView):
    template_name = 'pages/business/business_menu.html'

    def get_context_data(self, **kwargs):
        context = super(BusinessMenuView, self).get_context_data(**kwargs)
        context['tab'] = self.kwargs['category']
        return context


class BusinessPartnershipsView(BusinessDetailMixin, TemplateView):
    template_name = 'pages/business/business_partnerships.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tab'] = 'partnerships'
        return context


class BusinessLocationsView(BusinessDetailMixin, TemplateView):
    template_name = 'pages/business/business_locations.html'

    def get_context_data(self, **kwargs):
        context = super(BusinessLocationsView, self).get_context_data(**kwargs)
        context['tab'] = 'locations'
        return context


class DispensaryInfoView(DetailView):
    template_name = 'pages/dispensary/dispensary_info.html'
    context_object_name = 'location'

    def get_object(self, queryset=None):
        return get_object_or_404(BusinessLocation, state_fk__abbreviation__iexact=self.kwargs.get('state').lower(),
                                 city_fk__full_name_slug__iexact=self.kwargs.get('city_slug').lower(),
                                 slug_name__iexact=self.kwargs.get('slug_name').lower(),
                                 removed_date=None)

    def get_context_data(self, **kwargs):
        context = super(DispensaryInfoView, self).get_context_data(**kwargs)
        location = self.get_object()
        context['business_id'] = location.business.id
        context['business_name'] = location.business.name
        context['location_id'] = location.id
        context['vt_id'] = self.request.GET.get('vt_id')
        context['active_state'] = location.state_fk
        context['active_city'] = location.city_fk
        context['meta_desc'] = location.meta_desc
        context['social_image'] = location.social_image.url if location.social_image else "https://s3.amazonaws.com/{}"

        if not self.request.user.is_authenticated():
            can_request_menu_update = True
            can_request_menu_update_reason = None
        else:
            (can_request_menu_update,
             can_request_menu_update_reason) = location.can_user_request_menu_update(self.request.user)

        (context['can_request_menu_update'],
         context['can_request_menu_update_reason']) = can_request_menu_update, can_request_menu_update_reason

        # if this came from Available At on SDP
        if self.request.GET.get('available_at'):
            event = Event.VIEW_DISP_AVAIL_AT
        # if user came from dispensaries featured list
        elif 'HTTP_REFERER'in self.request.META and \
                urllib.parse.urlparse(self.request.META['HTTP_REFERER']).path == \
                reverse('businesses:dispensaries_list'):
            event = Event.FEATURED_CLICK
        else:
            event = Event.VIEW_DISP

        Analytics.track(
            event=event,
            user=self.request.user,
            entity_id=location.business.id
        )

        return context


class DispensariesInfoView(TemplateView):
    template_name = 'pages/locations/locations_list.html'

    def get_context_data(self, **kwargs):
        context = super(DispensariesInfoView, self).get_context_data(**kwargs)
        context['states'] = State.objects.filter(
            business_locations__dispensary=True,
            active=True
        ).order_by('abbreviation').distinct('abbreviation')

        user_location = self.request.user.get_location()
        if user_location:
            location = {
                'latitude': user_location.lat,
                'longitude': user_location.lng,
                'zip_code': user_location.zipcode
            }
        else:
            location = {}

        featured = FeaturedBusinessLocationService().get_list(**location)

        # Create events for analytics
        Event.objects.bulk_create([
            Analytics.track(
                event=Event.FEATURED_DISP,
                user=self.request.user,
                entity_id=featured_location.business_id,
                commit=False
            ) for featured_location in featured]
        )

        context['default_image_url'] = BusinessLocation.DEFAULT_IMAGE_URL
        context['featured'] = featured
        context['location_update'] = True

        context['location_type'] = 'dispensary'
        context['location_type_plural'] = 'dispensaries'

        return context


class DispensariesStatesView(TemplateView):
    template_name = 'pages/locations/locations_state_list.html'

    def get_context_data(self, **kwargs):
        context = super(DispensariesStatesView, self).get_context_data(**kwargs)
        if State.objects.filter(abbreviation__iexact=kwargs.get('state').lower()).exists():
            active_state = State.objects.get(abbreviation__iexact=kwargs.get('state').lower())
            context['active_state'] = active_state
            cities = City.objects.filter(
                state=active_state,
                business_locations__dispensary=True,
            ).order_by('full_name').distinct('full_name')
            context['cities_paged'] = NamePaginator(cities, on='full_name', per_page=10000)

            context['location_type'] = 'dispensary'
            context['location_type_plural'] = 'dispensaries'
        else:
            raise Http404
        return context


class DispensariesCitiesView(TemplateView):
    template_name = 'pages/locations/locations_city_list.html'

    def get_context_data(self, **kwargs):
        context = super(DispensariesCitiesView, self).get_context_data(**kwargs)
        if City.objects.filter(state__abbreviation__iexact=kwargs.get('state').lower(),
                               full_name_slug=kwargs.get('city_slug')).exists():

            active_state = State.objects.get(abbreviation__iexact=kwargs.get('state').lower())
            active_city = City.objects.get(state=active_state, full_name_slug=kwargs.get('city_slug'))
            context['active_state'] = active_state
            context['active_city'] = active_city

            context['location_type'] = 'dispensary'
            context['location_type_plural'] = 'dispensaries'
        else:
            raise Http404

        return context


class DispensaryRedirectView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('businesses:dispensaries_list')


class GrowersInfoView(TemplateView):
    template_name = 'pages/locations/locations_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['states'] = State.objects.filter(
            active=True,
            business_locations__grow_house=True,
        ).order_by('abbreviation').distinct('abbreviation')

        context['default_image_url'] = BusinessLocation.DEFAULT_IMAGE_URL
        context['location_update'] = True

        context['location_type'] = 'grower'
        context['location_type_plural'] = 'growers'

        return context


class GrowersStatesView(TemplateView):
    template_name = 'pages/locations/locations_state_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if State.objects.filter(abbreviation__iexact=kwargs.get('state').lower()).exists():
            active_state = State.objects.get(
                abbreviation__iexact=kwargs.get('state').lower(),
            )

            context['active_state'] = active_state
            cities = City.objects.filter(
                state=active_state,
                business_locations__grow_house=True,
            ).order_by('full_name').distinct('full_name')

            context['cities_paged'] = NamePaginator(cities, on='full_name', per_page=10000)

            context['location_type'] = 'grower'
            context['location_type_plural'] = 'growers'
        else:
            raise Http404
        return context


class GrowersCitiesView(TemplateView):
    template_name = 'pages/locations/locations_city_list.html'

    def get_context_data(self, **kwargs):
        context = super(GrowersCitiesView, self).get_context_data(**kwargs)
        if City.objects.filter(state__abbreviation__iexact=kwargs.get('state').lower(),
                               full_name_slug=kwargs.get('city_slug')).exists():

            active_state = State.objects.get(abbreviation__iexact=kwargs.get('state').lower())
            active_city = City.objects.get(state=active_state, full_name_slug=kwargs.get('city_slug'))
            context['active_state'] = active_state
            context['active_city'] = active_city

            context['location_type'] = 'grower'
            context['location_type_plural'] = 'growers'
        else:
            raise Http404

        return context


class GrowerInfoView(TemplateView):
    template_name = 'pages/grower/grower_info.html'

    def get_context_data(self, **kwargs):
        query_kwargs = {
            'grow_house': True,
            'state_fk__abbreviation__iexact': kwargs['state'],
            'city_fk__full_name_slug__iexact': kwargs['city_slug'],
            'slug_name__iexact': kwargs['slug_name'],
            'removed_date__isnull': True,
        }
        try:
            grower = BusinessLocation.objects.select_related('city_fk', 'state_fk', 'business').get(**query_kwargs)
        except BusinessLocation.DoesNotExist:
            raise Http404

        context = super().get_context_data(**kwargs)
        context['grower'] = grower
        menu = get_vts_and_images_for_location(grower)

        context['menu'] = menu

        grow_details = (
            ('organic', 'Organic', 'images/grow/organic.png'),
            ('pesticide_free', 'Pesticide Free Method', 'images/grow/pesticide_free.png'),
            ('indoor', 'Indoor', 'images/grow/indoor.png'),
            ('outdoor', 'Outdoor', 'images/grow/indoor.png'),
            ('lab_tested', 'Lab Tested', 'images/grow/lab_tested.png'),
        )
        context['grow_details'] = [(name, static(url)) for (key, name, url)
                                   in grow_details
                                   if grower.grow_details and grower.grow_details.get(key)]

        return context


class BusinessAnalyticsView(BusinessDetailMixin, FormView):
    template_name = 'pages/business/business_analytics.html'
    form_class = AnalyticsFilterForm

    def get(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_object(self):
        return get_object_or_404(Business, pk=self.kwargs.get('business_id'), users=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['data'] = self.request.GET
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        business = self.get_object()
        context['locations'] = BusinessLocation.objects.filter(business=business, removed_date=None).order_by('id')

        # analytics
        form = context['form']
        from_date = form.cleaned_data['from_date']
        to_date = form.cleaned_data['to_date']
        business_id = self.kwargs.get('business_id')

        # update request data
        update_request_data = BusinessLocationMenuUpdateRequest.objects\
            .events(from_date, to_date, business_id)

        # out of stock
        out_of_stock = ReportOutOfStock.objects\
            .events(from_date, to_date, business_id)

        context["total_page_views"] = Event.objects\
            .events(from_date, to_date, business_id, [Event.VIEW_DISP, Event.VIEW_DISP_AVAIL_AT, Event.DISP_LOOKUP]) \
            .count()
        context["total_calls"] = Event.objects\
            .events(from_date, to_date, business_id, Event.DISP_CALL).count()
        context["total_directions"] = Event.objects\
            .events(from_date, to_date, business_id, Event.DISP_GETDIR).count()
        context['total_update_request'] = update_request_data.count()
        context['total_out_of_stock'] = out_of_stock.count()
        context['total_featured'] = Event.objects.events(from_date, to_date, business_id,
                                                         [Event.FEATURED_CLICK, Event.FEATURED_DISP]).count()

        # lookup event data
        context['chart_lookup'] = Event.objects.events(from_date, to_date, business_id,
                                                       Event.DISP_LOOKUP).group_by_date()
        context['chart_lookup_action'] = Event.objects\
            .events(from_date, to_date, business_id, (Event.DISP_CALL, Event.DISP_GETDIR))\
            .group_by_date()
        # search event data
        context['chart_search'] = Event.objects.events(
            from_date, to_date, business_id, Event.VIEW_DISP_AVAIL_AT).group_by_date()
        context['chart_update_request_data'] = update_request_data.group_by_day()
        context['chart_out_of_stock'] = out_of_stock.group_by_day()
        # impressions - total times a dispensary page was seen
        context['chart_featured_impression'] = Event.objects\
            .events(from_date, to_date, business_id, Event.FEATURED_DISP)\
            .group_by_date()
        # views - total times when user clicks on dispensary in featured list
        context['chart_featured_view'] = Event.objects\
            .events(from_date, to_date, business_id, Event.FEATURED_CLICK)\
            .group_by_date()

        context['business'] = business
        context['tab'] = 'analytics'

        return context


class ClaimOptionsView(TemplateView):
    template_name = 'pages/business/claim_options.html'


class ClaimFormView(FormView):
    form_class = ClaimForm
    template_name = 'pages/business/claim_form.html'
    success_url = '/businesses/claim_success/'

    def form_valid(self, form):
        EmailService().send_business_claim_request_served_email(form.cleaned_data)
        return super().form_valid(form)


class ClaimSuccessView(TemplateView):
    template_name = 'pages/business/claim_success.html'
