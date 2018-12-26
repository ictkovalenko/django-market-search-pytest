import json
from django import template

from web.users.api.serializers import UserSerializer

register = template.Library()


@register.filter()
def userify(user):
    '''
    Template filter for returning json serialized user instance to JS
    :param user:
    :return:
    '''
    user = UserSerializer(user)

    return json.dumps(user.data)
