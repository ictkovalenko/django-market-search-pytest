# coding: utf-8
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, get_object_or_404

from web.businesses.models import Business


def user_is_owner(function):
    def wrap(request, *args, **kwargs):
        business_id = kwargs.get('business_id')
        business = get_object_or_404(Business, pk=business_id)

        if request.user.id != business.created_by.id:
            return redirect('/')

        if not request.user.is_email_verified:
            return redirect(reverse('businesses:signup_done'))

        return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def authorized_for_signup(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect('/')

        return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
