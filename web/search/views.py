# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json
from urllib.parse import urlparse

from django.core.urlresolvers import reverse, resolve, Resolver404
from django.db.models import Q
from django.http import Http404
from django.views.generic import TemplateView

from web.search.api.serializers import VtSearchSerializer
from web.search.models import Vt, VtImage


class VtSearchWizardView(TemplateView):
    template_name = 'pages/search/vt/wizard.html'


class VtSearchView(TemplateView):
    template_name = 'pages/search/vt/search.html'


class VtAdvancedSearchView(TemplateView):
    template_name = 'pages/search/vt/advanced_search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        serializer = VtSearchSerializer(data=self.request.GET)
        serializer.is_valid(raise_exception=False)
        context['form'] = serializer
        return context


class VtAdvancedSearchResultView(TemplateView):
    template_name = 'pages/search/vt/advanced_search_results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_url'] = reverse('search:search') if self.request.GET.get('q') else \
            reverse('search:advanced_search')
        context['terpenes_abbreviation'] = json.dumps(VtSearchSerializer.TERPENES_ABBREVIATION)
        return context


class VtSearchResultView(TemplateView):
    template_name = 'pages/search/vt/search_results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sign_in_url'] = '{url}?next={next_url}'.format(
            url=reverse('account_login'),
            next_url=reverse('search:vt_results'),
        )
        return context


class VtDetailView(TemplateView):
    template_name = 'pages/vt/vt_detail.html'

    def get_context_data(self, **kwargs):
        context = super(VtDetailView, self).get_context_data(**kwargs)

        slug_name = kwargs.get('slug_name')
        vt_variety = kwargs.get('vt_variety')

        try:
            vt = Vt.objects.get(variety=vt_variety, vt_slug=slug_name)
        except Vt.DoesNotExist:
            raise Http404

        context['vt_id'] = vt.id
        context['vt_name'] = vt.name
        context['vt_variety'] = vt.variety
        context['social_desc'] = vt.meta_desc
        context['social_image'] = vt.social_image.url if vt.social_image else "https://s3.amazonaws.com/{}"
        context['from_location'] = self.get_previous_location_url()

        return context

    def get_previous_location_url(self):
        referrer = self.request.META.get('HTTP_REFERER')

        if referrer is None:
            return None

        path = urlparse(referrer).path
        try:
            match = resolve(path)
        except Resolver404:
            return None

        if match.url_name == 'dispensary_info':
            return path

        return None


class VtsRootView(TemplateView):
    template_name = 'pages/vt/vts_root.html'


class VtsSativaRootView(TemplateView):
    template_name = 'pages/vt/vts_sativa_root.html'


class VtsIndicaRootView(TemplateView):
    template_name = 'pages/vt/vts_indica_root.html'


class VtsHybridRootView(TemplateView):
    template_name = 'pages/vt/vts_hybrid_root.html'


class VtsByNameView(TemplateView):
    template_name = 'pages/vt/vts_name_paged.html'

    def get_context_data(self, **kwargs):
        context = super(VtsByNameView, self).get_context_data(**kwargs)

        vt_variety = kwargs.get('vt_variety')
        current_letter = kwargs.get('letter')
        paging_letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
                          'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        paging_letters_len = len(paging_letters)

        for i, l in enumerate(paging_letters):
            if l == current_letter:
                if i - 1 >= 0:
                    context['prev_letter'] = paging_letters[i - 1]
                if i + 1 < paging_letters_len:
                    context['next_letter'] = paging_letters[i + 1]
                break

        if current_letter == 'other':
            query = Q()
            for letter in paging_letters:
                query = query | Q(name__istartswith=letter)

            vts = Vt.objects.filter(variety=vt_variety).exclude(query).order_by('name')
            context['prev_letter'] = 'z'
        else:
            vts = Vt.objects.filter(variety=vt_variety, name__istartswith=current_letter).order_by('name')

        transformed = []
        for s in vts:
            vt_image = VtImage.objects.filter(vt=s.id, is_approved=True)[:1]
            vt_image = vt_image[0].image.url if len(vt_image) > 0 else None
            transformed.append({'vt': s, 'vt_image': vt_image})

        context['vts'] = transformed
        context['current_letter'] = current_letter
        context['variety'] = vt_variety
        return context
