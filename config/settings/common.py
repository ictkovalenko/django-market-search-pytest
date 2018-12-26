# -*- coding: utf-8 -*-
"""
Django settings for web project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""
from __future__ import absolute_import, unicode_literals

import os

import environ
import raven
from boto.s3.connection import OrdinaryCallingFormat

gettext = lambda s: s

ROOT_DIR = environ.Path(__file__) - 3  # (web/config/settings/common.py - 3 = web/)
APPS_DIR = ROOT_DIR.path('web')

env = environ.Env()
env.read_env('.env')

# APP CONFIGURATION
# ------------------------------------------------------------------------------
DJANGO_APPS = (
    # Default Django apps:
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'static_sitemaps',

    # Useful template tags:
    # 'django.contrib.humanize',

    # Admin
    'django.contrib.admin',
)
THIRD_PARTY_APPS = (
    'crispy_forms',  # Form layouts
    'allauth',  # registration
    'allauth.account',  # registration
    'allauth.socialaccount',  # registration
    'rest_framework',  # API,
    'storages',
    'raven.contrib.django.raven_compat',
    'tinymce',
    'corsheaders',
    'rangefilter',
    'impersonate',
    'django_json_widget',
)

# Apps specific for this project go here.
LOCAL_APPS = (
    # custom users app
    'web.users.apps.UsersConfig',
    'web.search.apps.SearchConfig',
    'web.businesses.apps.BusinessConfig',
    'web.system.apps.SystemConfig',
    'web.articles.apps.ArticlesConfig',
    'web.analytics.apps.AnalyticsConfig',
    # Your stuff: custom apps go here
    'web',

    # cms admin
    'cms',
    'menus',
    'treebeard',
    'djangocms_text_ckeditor',
    'filer',
    'ckeditor_filebrowser_filer',
    'easy_thumbnails',

)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# MIDDLEWARE CONFIGURATION
# ------------------------------------------------------------------------------
MIDDLEWARE_CLASSES = (
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'web.common.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'web.common.middleware.TimezoneMiddleware',
    'web.common.middleware.ImpersonateMiddleware',
)

CORS_ORIGIN_WHITELIST = (
    'staging.',
    '',
    's3.amazonaws.com',
)

# MIGRATIONS CONFIGURATION
# ------------------------------------------------------------------------------
MIGRATION_MODULES = {
    'sites': 'web.contrib.sites.migrations'
}

# DEBUG
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool('DJANGO_DEBUG', False)

# FIXTURE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-FIXTURE_DIRS
FIXTURE_DIRS = (
    str(APPS_DIR.path('fixtures')),
)

# EMAIL CONFIGURATION
# ------------------------------------------------------------------------------
EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')

# MANAGER CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = (
    ("""Vt Tech""", 'tech@'),
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS

# DATABASE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': env('DB_NAME', default=''),
        'USER': env('DB_USER', default=''),
        'PASSWORD': env('DB_PASSWORD', default=''),
        'HOST': env('DB_HOST', default=''),
        'PORT': env('DB_PORT', default='5432'),
    }
}
DATABASES['default']['ATOMIC_REQUESTS'] = True

# GENERAL CONFIGURATION
# ------------------------------------------------------------------------------
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'UTC'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = 'en'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True

# TEMPLATE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        'DIRS': [
            str(APPS_DIR.path('templates')),
        ],
        'OPTIONS': {
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
            'debug': DEBUG,
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                # Your stuff: custom template context processors go here
            ],
        },
    },
]

# See: http://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# STATIC FILE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(ROOT_DIR('staticfiles'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'
STATICSITEMAPS_ROOT_SITEMAP = 'config.urls.sitemaps'

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = (
    str(APPS_DIR.path('static')),
    str(ROOT_DIR.path('node_modules')),
)

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# MEDIA CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(APPS_DIR('media'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = '/media/'

# URL Configuration
# ------------------------------------------------------------------------------
ROOT_URLCONF = 'config.urls'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = 'config.wsgi.application'

# AUTHENTICATION CONFIGURATION
# ------------------------------------------------------------------------------
# AUTHENTICATION_BACKENDS = (
#     'django.contrib.auth.backends.ModelBackend',
#     'allauth.account.auth_backends.AuthenticationBackend',
# )

AUTHENTICATION_BACKENDS = (
    'web.common.email_auth.EmailBackend',
)

# Some really nice defaults
ACCOUNT_AUTHENTICATION_METHOD = 'username'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'

ACCOUNT_ALLOW_REGISTRATION = env.bool('DJANGO_ACCOUNT_ALLOW_REGISTRATION', True)
ACCOUNT_ADAPTER = 'web.users.adapters.AccountAdapter'
SOCIALACCOUNT_ADAPTER = 'web.users.adapters.SocialAccountAdapter'

# Custom user app defaults
# Select the correct user model
AUTH_USER_MODEL = 'users.User'
LOGIN_REDIRECT_URL = 'users:redirect'
LOGIN_URL = 'account_login'

# time when user will be redirected to search result page after email confirmation
REDIRECT_SEARCH_RESULT_TIME = 8  # minutes

# SLUGLIFIER
AUTOSLUG_SLUGIFY_FUNCTION = 'slugify.slugify'

# django-compressor
# ------------------------------------------------------------------------------


# Location of root django.contrib.admin URL, use {% url 'admin:index' %}
ADMIN_URL = r'^admin/'

# Your common stuff: Below this line define 3rd party library settings
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
    )
}

LOGGER_NAME = 'web'

MAX_VT_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_BUSINESS_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB

DEFAULT_DELIVERY_RADIUS = 10

SENDGRID_API_KEY = env('SENDGRID_API_KEY', default='')
DEFAULT_FROM_EMAIL = 'support@'
CC_DEFAULT_EMAIL = env('CC_DEFAULT_EMAIL', default='support@')

HOST = env('HOST_URL', default='http://localhost:8000')

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

# Elasticsearch
ELASTICSEARCH_URL = env('ELASTICSEARCH_URL', default='')
ELASTICSEARCH_USERNAME = env('ELASTICSEARCH_USERNAME', default='')
ELASTICSEARCH_PASSWORD = env('ELASTICSEARCH_PASSWORD', default='')

# AWS
AWS_ACCESS_KEY_ID = env('DJANGO_AWS_ACCESS_KEY_ID', default='')
AWS_SECRET_ACCESS_KEY = env('DJANGO_AWS_SECRET_ACCESS_KEY', default='')
AWS_STORAGE_BUCKET_NAME = env('DJANGO_AWS_STORAGE_BUCKET_NAME', default='')
AWS_AUTO_CREATE_BUCKET = False
AWS_S3_SECURE_URLS = True  # use http if False
AWS_QUERYSTRING_AUTH = False  # don't add complex authentication-related query parameters for requests
AWS_S3_CALLING_FORMAT = OrdinaryCallingFormat()

# HTTP auth
HTTP_USERNAME = env('SRX_HTTP_USERNAME', default='')
HTTP_PASSWORD = env('SRX_HTTP_PASSWORD', default='')

# GOOGLE
GOOGLE_API_KEY = env('SRX_GOOGLE_API_KEY', default='')

SERVER_ENV = env('SERVER_ENV', default='dev')

RAVEN_CONFIG = {
    'dsn': env('SENTRY_DSN', default=''),
    # If you are using git, you can also automatically configure the
    # release based on the git info.
    'release': raven.fetch_git_sha(os.path.dirname(APPS_DIR)),
    'environment': SERVER_ENV
}

# LOGGING CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#logging
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)s [%(funcName)s:%(process)d] %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            'tags': {
                'environment': SERVER_ENV
            }
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': os.path.join(str(ROOT_DIR), 'srx_error.log')
        }
    },
    'loggers': {
        'web': {
            'level': 'DEBUG',
            'formatter': 'verbose',
            'handlers': ['sentry', 'file']
        },
        'django.request': {
            'handlers': ['file'],
            'level': 'ERROR',
            'formatter': 'verbose',
            'propagate': True
        },
        'django.security.DisallowedHost': {
            'level': 'ERROR',
            'handlers': ['console', 'file'],
            'formatter': 'verbose',
            'propagate': True
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
            'formatter': 'verbose',
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
            'formatter': 'verbose',
            'propagate': False,
        },
    }
}

PROFILE = 'local'

TINYMCE_DEFAULT_CONFIG = {
    'theme': "advanced",
    'custom_undo_redo_levels': 10,
    "inline_styles": False
}

TINYMCE_JS_ROOT = '/tinymce-static'
TINYMCE_JS_URL = '/tinymce-static/tiny_mce/tiny_mce.js'

APPEND_SLASH = True

# START CMS SETTINGS
LANGUAGES = (
    ## Customize this
    ('en', gettext('en')),
)

CMS_LANGUAGES = {
    ## Customize this
    1: [
        {
            'name': gettext('en'),
            'hide_untranslated': False,
            'redirect_on_fallback': True,
            'public': True,
            'code': 'en',
        },
    ],
    'default': {
        'hide_untranslated': False,
        'public': True,
        'redirect_on_fallback': True,
    },
}

CMS_TEMPLATES = (
    ## Customize this
    ('fullwidth.html', 'Fullwidth'),
    ('homepage.html', 'Home Page'),
    ('sidebar_left.html', 'Sidebar Left'),
    ('sidebar_right.html', 'Sidebar Right')
)

CMS_PERMISSION = True

CMS_PLACEHOLDER_CONF = {}

MAX_IMAGE_SIZE = 10 * 1024 * 1024 #10mb

CKEDITOR_SETTINGS = {
    'language': '{{ language }}',
    'toolbar': [
        ['Undo', 'Redo'],
        ['Styles', 'Format', 'Font', 'FontSize'],
        ['TextColor', 'BGColor'],
        ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat'],
        ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
        ['Source'],
        ['Find', 'Replace', '-', 'SelectAll'],
        ['FilerImage']
    ],
    'skin': 'moono',
    'extraPlugins': 'filerimage',
}

# CKEditor is used only in admin, so we can be permissive
TEXT_ADDITIONAL_ATTRIBUTES = ('*', 'placeholder')

# END CMS SETTINGS

FB_PROFILE_URL = 'https://www.facebook.com/{}/'

PERIOD_OUT_OF_STOCK = env.int('PERIOD_OUT_OF_STOCK', 7)  # Period in days from first report as out of stock
# Period in days when menu item marks as out of stock after second report
PERIOD_BLOCK_MENU_ITEM_OUT_OF_STOCK = env.int('PERIOD_BLOCK_MENU_ITEM_OUT_OF_STOCK', 10)

PIPENV_TIMEOUT = 240