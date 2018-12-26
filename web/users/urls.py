# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from web.users.decorators import user_is_owner, authorized_for_signup
from . import views

urlpatterns = [
    url(
        regex=r'^$',
        view=views.UserListView.as_view(),
        name='list'
    ),
    url(
        regex=r'^~redirect/$',
        view=views.UserRedirectView.as_view(),
        name='redirect'
    ),
    url(
        regex=r'^confirm_email/(?P<uid>[0-9]{1,})/$',
        view=views.ConfirmEmailView.as_view(),
        name='confirm_email'
    ),
    url(
        regex=r'^(?P<user_id>[0-9]{1,})/$',
        view=user_is_owner(views.UserDetailView.as_view()),
        name='detail',
    ),
    url(
        regex=r'^(?P<user_id>[0-9]{1,})/favorites$',
        view=user_is_owner(views.UserFavoritesView.as_view()),
        name='favorites'
    ),
    url(
        regex=r'^(?P<user_id>[0-9]{1,})/reviews',
        view=user_is_owner(views.UserReviewsView.as_view()),
        name='reviews'
    ),
    url(
        regex=r'^(?P<user_id>[0-9]{1,})/notifications',
        view=user_is_owner(views.UserNotificationsView.as_view()),
        name='notifications'
    ),
    url(
        regex=r'^(?P<user_id>[0-9]{1,})/proximity',
        view=user_is_owner(views.UserProximitySettingsView.as_view()),
        name='proximity'
    ),
    url(
        regex=r'^(?P<user_id>[0-9]{1,})/pwd',
        view=user_is_owner(views.UserChangePwdView.as_view()),
        name='change_pwd'
    ),
    url(
        regex=r'^~update/$',
        view=views.UserUpdateView.as_view(),
        name='update'
    ),
    url(
        regex=r'^signup/done/$',
        view=views.UserSignUpDoneView.as_view(),
        name='signup_done'
    ),
    url(
        regex=r'^signup/wizard/$',
        view=authorized_for_signup(views.UserSignUpWizardView.as_view()),
        name='signup'
    ),
    url(
        regex=r'^impersonate/(?P<uid>.+)/$',
        view=views.ImpersonateView.as_view(),
        name='impersonate-start'
    ),
]
