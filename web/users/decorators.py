# coding: utf-8
from django.shortcuts import redirect


def user_is_owner(function):
    def wrap(request, *args, **kwargs):
        if request.user.id != int(kwargs.get('user_id')):
            return redirect('/')

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
