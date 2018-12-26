import logging
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import truncatechars
from django.utils import timezone
from django.utils.text import slugify
from django_resized import ResizedImageField
from djangocms_text_ckeditor.fields import HTMLField

logger = logging.getLogger(__name__)


def upload_to(instance, filename):
    path = 'articles/{0}_{1}'.format(uuid4(), filename)
    return path


def validate_image(field_file_obj):
    try:
        file_size = field_file_obj.file.size
        megabyte_limit = settings.MAX_IMAGE_SIZE
        if file_size > megabyte_limit:
            raise ValidationError('Max file size is {}MB'.format(megabyte_limit))
    except OSError:
        raise ValidationError('File does not exists.')


class Category(models.Model):
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='subcategories')
    title = models.CharField(max_length=256, unique=True, blank=False)
    is_active = models.BooleanField(default=True)
    slug = models.SlugField(max_length=1024, unique=True, blank=True)

    def __str__(self):
        return self.title

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_data = {'slug': self.slug, 'parent': self.parent}

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Category, self).save(*args, **kwargs)

    @property
    def url(self):
        if self.parent:
            return '{}/{}'.format(self.parent.url, self.slug)
        return self.slug


class Article(models.Model):
    title = models.CharField(max_length=1024, unique=True, blank=False)
    summary = models.CharField(max_length=3072, blank=True)
    meta_desc = models.CharField(max_length=3072, blank=True)
    meta_keywords = models.CharField(max_length=3072, blank=True)
    text = HTMLField(blank=True)
    is_sponsored = models.BooleanField(default=False)
    featured = models.IntegerField(blank=True, null=True)
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(null=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, null=True, blank=True, verbose_name='Category', related_name='articles')
    image = ResizedImageField(max_length=255, blank=True, help_text='Maximum file size allowed is 10Mb',
                              validators=[validate_image], quality=75, size=[1024, 1024], upload_to=upload_to)
    image_caption = models.CharField(max_length=1024, blank=True)
    slug = models.SlugField(max_length=1024, blank=True, unique=True)

    def __str__(self):
        return self.title

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_data = {'slug': self.slug, 'category_slug': self.category.slug if self.category else None}

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Article, self).save(*args, **kwargs)

    def get_absolute_url(self):
        if self.category:
            return reverse('view_article', kwargs={'category_slug': self.category.url, 'article_slug': self.slug})
        return reverse('view_page', args=(self.slug,))

    @property
    def short_title(self):
        return truncatechars(self.title, 75)
