from django.conf.urls import url

from web.search.api.views import *

urlpatterns = [
    url(
        regex=r'^effect/(?P<effect_type>[a-z_]+)$',
        view=VtEffectView.as_view(),
        name='effect_type'
    ),
    url(
        regex=r'^flavors$',
        view=VtFlavorView.as_view(),
        name='flavors'
    ),
    url(
        regex=r'^vts/(?P<vt_variety>.+)$',
        view=VtsListByVarietyView.as_view(),
        name='vts_list'
    ),
    url(
        regex=r'^vt/(?P<vt_id>[0-9]+)/images/$',
        view=VtImagesView.as_view(),
        name='vt_images'
    ),
    url(
        regex=r'^vt/(?P<vt_id>[0-9]+)/rate',
        view=VtRateView.as_view(),
        name='vt_rate'
    ),
    url(
        regex=r'^vt/(?P<vt_id>[0-9]+)/details',
        view=VtDetailsView.as_view(),
        name='vt_details'
    ),
    url(
        regex=r'^vt/(?P<vt_id>[0-9]+)/deliveries',
        view=VtDeliveriesView.as_view(),
        name='vt_deliveries'
    ),
    url(
        regex=r'^vt/(?P<vt_id>[0-9]+)/reviews',
        view=VtReviewsView.as_view(),
        name='vt_reviews'
    ),
    url(
        regex=r'^vt/(?P<vt_id>[0-9]+)/ratings',
        view=VtRatingsView.as_view(),
        name='vt_ratings'
    ),
    url(
        regex=r'^vt/(?P<vt_id>[0-9]+)/favorite',
        view=VtFavoriteView.as_view(),
        name='vt_favorite'
    ),
    url(
        regex=r'^vt/(?P<vt_id>[0-9]+)/srx_score',
        view=VtSRXScoreView.as_view(),
        name='vt_srx_score'
    ),
    url(
        regex=r'^vt/(?P<vt_id>[0-9]+)/also_like',
        view=VtAlsoLikeView.as_view(),
        name='vt_also_like'
    ),
    url(
        regex=r'^vt/lookup/$',
        view=VtLookupView.as_view(),
        name='vt_lookup'
    ),
    url(
        regex=r'^vt',
        view=VtSearchWizardView.as_view(),
        name='vt'
    ),
    url(
        regex=r'^result/$',
        view=VtSearchResultsView.as_view(),
        name='vt_result'
    ),
    url(
        regex=r'^(?P<bus_type>dispensary|grow_house)/lookup/$',
        view=BusinessLocationLookupView.as_view(),
        name='dispensary_lookup'
    ),
    url(
        regex=r'^search/$',
        view=VtSearchAPIView.as_view(),
        name='search'
    ),
]
