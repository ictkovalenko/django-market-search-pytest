# -*- coding: utf-8 -*-
from django.conf.urls import url

from web.analytics.api.views import *

urlpatterns = [
    url(
        regex=r'^track',
        view=AnalyticsTrackView.as_view(),
        name='track_event'
    ),
]
