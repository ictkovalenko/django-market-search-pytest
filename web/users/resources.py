from __future__ import absolute_import, unicode_literals

from django.contrib.auth import get_user_model
from import_export import resources


class UserResource(resources.ModelResource):
    class Meta:
        model = get_user_model()
        fields = ('email', 'first_name', 'last_name', 'type', 'last_login',
                  'date_joined', 'is_email_verified', 'is_superuser')
        export_order = ('email', 'first_name', 'last_name', 'type', 'last_login',
                        'date_joined', 'is_email_verified', 'is_superuser')
        widgets = {
            'last_login': {'format': '%b %d %Y %I:%M %p'},
            'date_joined': {'format': '%b %d %Y %I:%M %p'},
        }
