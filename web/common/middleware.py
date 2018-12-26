import pytz
from django.contrib import auth
from django.utils import timezone
from django.utils.functional import SimpleLazyObject
from impersonate.helpers import is_authenticated, User, check_allow_for_user, check_allow_for_uri
from impersonate.middleware import ImpersonateMiddleware as BaseImpersonateMiddleware

from web.users.models import CustomAnonymousUser


class ImpersonateMiddleware(BaseImpersonateMiddleware):

    def process_request(self, request):
        request.user.is_impersonate = False
        request.impersonator = None

        if is_authenticated(request.user) and \
           '_impersonate' in request.session:
            new_user_id = request.session['_impersonate']
            if isinstance(new_user_id, User):
                # Edge case for issue 15
                new_user_id = new_user_id.pk

            try:
                new_user = User.objects.get(pk=new_user_id)
            except User.DoesNotExist:
                return

            if check_allow_for_user(request, new_user) and \
               check_allow_for_uri(request.path):
                request.impersonator = request.user
                request.user = new_user
                request.user.is_impersonate = True

                # Add user attribute for django-rest-framework
                request._user = new_user

        request.real_user = request.impersonator or request.user


class TimezoneMiddleware(object):
    def process_request(self, request):
        user = request.user
        if user.is_authenticated():
            tzname = user.timezone
            if tzname:
                timezone.activate(pytz.timezone(tzname))
            else:
                timezone.deactivate()

        return None


class AuthenticationMiddleware(object):

    def get_user(self, request):
        if not hasattr(request, '_cached_user'):
            user = auth.get_user(request)
            if user.is_anonymous():
                user = CustomAnonymousUser(request)

            request._cached_user = user
        return request._cached_user

    def process_request(self, request):
        assert hasattr(request, 'session'), (
            "The Django authentication middleware requires session middleware "
            "to be installed. Edit your MIDDLEWARE_CLASSES setting to insert "
            "'django.contrib.sessions.middleware.SessionMiddleware' before "
            "'django.contrib.auth.middleware.AuthenticationMiddleware'."
        )
        request.user = SimpleLazyObject(lambda: self.get_user(request))
        request._user = SimpleLazyObject(lambda: self.get_user(request))
