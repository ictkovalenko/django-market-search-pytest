from django.http import HttpResponsePermanentRedirect
from django.template.response import TemplateResponse
from django.views.decorators.csrf import requires_csrf_token
from django.views.defaults import page_not_found
from rest_framework import status

from web.system.models import PermanentlyRemoved


@requires_csrf_token
def page_404_handler(request, exception, template_name='404.html'):
    instance = PermanentlyRemoved.objects.filter(url__iexact=request.path).first()
    if instance:
        if instance.status == status.HTTP_301_MOVED_PERMANENTLY:
            return HttpResponsePermanentRedirect(instance.redirect_url)
        return TemplateResponse(request, '410.html', status=410)
    return page_not_found(request, exception, template_name)
