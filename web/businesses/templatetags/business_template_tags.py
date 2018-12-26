import dateutil.parser
from django import template
from django.utils import formats

register = template.Library()


@register.simple_tag
def to_active_since_date(iso_date_string):
    date = dateutil.parser.parse(iso_date_string)
    return formats.date_format(date, 'F Y')
