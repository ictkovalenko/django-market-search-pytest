# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals
from django.utils import six
from .common import *  # noqa

# these two must be set before the backend can init for S3:
#   django.core.exceptions.ImproperlyConfigured: The SECRET_KEY setting must not be empty.
#   CommandError: You must set settings.ALLOWED_HOSTS if DEBUG is False.
SECRET_KEY = env('DJANGO_SECRET_KEY')
ALLOWED_HOSTS = ['*']

from storages.backends.s3boto import S3BotoStorage
from web.custom_s3_boto_storage import StaticS3Storage

ANYMAIL = {}
AWS_EXPIRY = 60 * 60 * 24 * 7
AWS_HEADERS = {'Cache-Control': six.b('max-age=%d, s-maxage=%d, must-revalidate' % (AWS_EXPIRY, AWS_EXPIRY))}
AWS_PRELOAD_METADATA = True
CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache', 'LOCATION': ''}}
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SECURE = True
DEBUG = True
DEFAULT_FILE_STORAGE = 'config.settings.stage.MediaRootS3BotoStorage'
DEFAULT_FROM_EMAIL = env('DJANGO_DEFAULT_FROM_EMAIL', default='web <noreply@example.com>')
EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_SUBJECT_PREFIX = env('DJANGO_EMAIL_SUBJECT_PREFIX', default='[web] ')
HOST = env('HOST_URL')
INSTALLED_APPS += ("anymail",)
MediaRootS3BotoStorage = lambda: S3BotoStorage(location='media')
MEDIA_URL = 'https://s3.amazonaws.com/%s/media/' % AWS_STORAGE_BUCKET_NAME
PROFILE = 'stage'
SECURE_REDIRECT_EXEMPT = []
SECURE_SSL_REDIRECT = False
SERVER_EMAIL = env('DJANGO_SERVER_EMAIL')
SESSION_COOKIE_HTTPONLY = False
SESSION_COOKIE_SECURE = True
STATICFILES_STORAGE = 'config.settings.stage.StaticRootS3BotoStorage'
StaticRootS3BotoStorage = lambda: StaticS3Storage(location='static')
STATIC_URL = 'https://s3.amazonaws.com/%s/static/' % AWS_STORAGE_BUCKET_NAME
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG
TEST_RUNNER = 'django.test.runner.DiscoverRunner'
X_FRAME_OPTIONS = 'SAMEDOMAIN'
PIPENV_TIMEOUT = 330