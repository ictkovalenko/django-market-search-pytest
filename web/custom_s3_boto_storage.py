# combine manifest cache bust with s3 storage http://www.kerseydev.com/2016/04/using-manifeststaticfilesstorage-django-storages-amazon-s3/
from django.contrib.staticfiles.storage import ManifestFilesMixin

from storages.backends.s3boto import S3BotoStorage

class StaticS3Storage(ManifestFilesMixin, S3BotoStorage):
    pass
