# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r'^search/results/$',
        view=views.VtAdvancedSearchResultView.as_view(),
        name='advanced_search_result'
    ),
    url(
        regex=r'^basic-search/$',
        view=views.VtSearchView.as_view(),
        name='search'
    ),
    url(
        regex=r'^advanced-search/$',
        view=views.VtAdvancedSearchView.as_view(),
        name='advanced_search'
    ),
    url(
        regex=r'^search/vt/wizard/$',
        view=views.VtSearchWizardView.as_view(),
        name='vt_wizard'
    ),
    url(
        regex=r'^search/vt/results/$',
        view=views.VtSearchResultView.as_view(),
        name='vt_results'
    ),
    url(
        regex=r'^vts/$',
        view=views.VtsRootView.as_view(),
        name='vts_root'
    ),
    url(
        regex=r'^vts/sativa/$',
        view=views.VtsSativaRootView.as_view(),
        name='vts_sativa_root'
    ),
    url(
        regex=r'^vts/indica/$',
        view=views.VtsIndicaRootView.as_view(),
        name='vts_indica_root'
    ),
    url(
        regex=r'^vts/hybrid/$',
        view=views.VtsHybridRootView.as_view(),
        name='vts_hybrid_root'
    ),
    url(
        regex=r'^vts/(?P<vt_variety>sativa|hybrid|indica)/list/(?P<letter>[a-z]+)/$',
        view=views.VtsByNameView.as_view(),
        name='vts_type_by_name'
    ),
    url(
        regex=r'^vts/(?P<vt_variety>sativa|hybrid|indica)/(?P<slug_name>.+)/$',
        view=views.VtDetailView.as_view(),
        name='vt_detail'
    ),
]
