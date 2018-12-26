from django.dispatch import receiver

from impersonate.signals import session_begin

from web.users.login import pre_login


@receiver(session_begin, dispatch_uid='web.users.signals.on_session_begin')
def on_session_begin(sender, impersonator, impersonating, request, **kwargs):
    """
    sender - this is a Django signal requirement, and is always set to None
    impersonator - a reference to the User object of the person doing the impersonation
    impersonating - a reference to the User object of the person being impersonated
    request - the Django HttpRequest object from which the impersonation was invoked
    :return:
    """
    pre_login(impersonating, request)
