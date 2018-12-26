from __future__ import unicode_literals, absolute_import

from datetime import datetime
from json import loads, dumps
from uuid import uuid4

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django_resized import ResizedImageField

from web.search.querysets import UserSearchQuerySet
from web.system.models import ReviewAbstract
from web.users.models import User


def upload_to(instance, filename):
    path = 'articles/{0}_{1}'.format(uuid4(), filename)
    return path


@python_2_unicode_compatible
class Vt(models.Model):

    VARIETY_CHOICES = (
        ('sativa', 'Sativa'),
        ('indica', 'Indica'),
        ('hybrid', 'Hybrid'),
    )

    CATEGORY_CHOICES = (
        ('flower', 'Flower'),
        ('edible', 'Edible'),
        ('liquid', 'Liquid'),
        ('oil', 'Oil'),
        ('wax', 'Wax'),
    )
    INDOOR_SOIL, INDOOR_HYDRO, INDOOR_COCO, OUTDOOR, GREENHOUSE, AQUAPONICS = range(1, 7)

    GROWING_METHOD_CHOICES = (
        (INDOOR_SOIL, 'Indoor Soil'),
        (INDOOR_HYDRO, 'Indoor Hydro'),
        (INDOOR_COCO, 'Indoor Coco'),
        (OUTDOOR, 'Outdoor'),
        (GREENHOUSE, 'Greenhouse'),
        (AQUAPONICS, 'Aquaponics'),
    )

    NATURAL, HID, LED, DOUBLE_ENDED, HALOGEN = range(1, 6)

    LIGHTING_CHOICES = (
        (NATURAL, 'Natural Light Schedule'),
        (HID, 'HID'),
        (LED, 'LED'),
        (DOUBLE_ENDED, 'Double Ended'),
        (HALOGEN, 'Halogen'),
    )

    SYNTHETIC, ORGANIC, BLENDED = range(1, 4)

    NUTRIENT_BASE_CHOICES = (
        (SYNTHETIC, 'Synthetic Nutrients'),
        (ORGANIC, 'Organic Nutrients'),
        (BLENDED, 'Blended Nutrients'),
    )

    def validate_image(self):
        file_size = self.file.size
        megabyte_limit = settings.MAX_IMAGE_SIZE
        if file_size > megabyte_limit:
            raise ValidationError("Max file size is %sMB" % str(megabyte_limit))

    internal_id = models.CharField(max_length=10, null=True, blank=True)
    name = models.CharField(max_length=255)
    common_name = models.CharField(max_length=255, null=True, blank=True)
    vt_slug = models.SlugField(max_length=611, null=True, blank=True,
                                   help_text='Warning: changing the slug will change the URL of this vt')

    variety = models.CharField(max_length=255, choices=VARIETY_CHOICES)
    category = models.CharField(max_length=255, choices=CATEGORY_CHOICES)

    effects = JSONField(default={"happy": 0, "uplifted": 0, "stimulated": 0, "energetic": 0,
                                 "creative": 0, "focused": 0, "relaxed": 0, "sleepy": 0, "talkative": 0,
                                 "euphoric": 0, "hungry": 0, "tingly": 0, "good_humored": 0})

    benefits = JSONField(default={"reduce_stress": 0, "help_depression": 0, "relieve_pain": 0, "reduce_fatigue": 0,
                                  "reduce_headaches": 0, "help_muscles_spasms": 0, "lower_eye_pressure": 0,
                                  "reduce_nausea": 0, "reduce_inflammation": 0, "relieve_cramps": 0,
                                  "help_with_seizures": 0, "restore_appetite": 0, "help_with_insomnia": 0})

    side_effects = JSONField(default={"anxiety": 0, "dry_mouth": 0, "paranoia": 0,
                                      "headache": 0, "dizziness": 0, "dry_eyes": 0,
                                      "spacey": 0, "lazy": 0, "hungry": 0, "groggy": 0})

    flavor = JSONField(default={"ammonia": 0, "apple": 0, "apricot": 0, "berry": 0, "blue-cheese": 0,
                                "blueberry": 0, "buttery": 0, "cheese": 0, "chemical": 0, "chestnut": 0,
                                "citrus": 0, "coffee": 0, "diesel": 0, "earthy": 0, "flowery": 0,
                                "grape": 0, "grapefruit": 0, "herbal": 0, "honey": 0, "lavender": 0,
                                "lemon": 0, "lime": 0, "mango": 0, "menthol": 0, "minty": 0,
                                "nutty": 0, "orange": 0, "peach": 0, "pear": 0, "pepper": 0,
                                "pine": 0, "pineapple": 0, "plum": 0, "pungent": 0, "rose": 0,
                                "sage": 0, "skunk": 0, "spicy-herbal": 0, "strawberry": 0, "sweet": 0,
                                "tar": 0, "tea": 0, "tobacco": 0, "tree-fruit": 0, "tropical": 0,
                                "vanilla": 0, "violet": 0, "woody": 0, "banana": 0, "cherry": 0, "chocolate": 0,
                                "sour": 0})
    # if new terpene is added we need to update VtSearchSerializer
    terpenes = JSONField(default={"humulene": 0, "pinene": 0, "linalool": 0, "caryophyllene": 0, "myrcene": 0,
                                  "terpinolene": 0, "ocimene": 0, "limonene": 0, "camphene": 0, "terpineol": 0,
                                  "phellandrene": 0, "carene": 0, "pulegone": 0, "sabinene": 0, "geraniol": 0,
                                  "valencene": 0})

    quick_picks = JSONField(default={"pain relief": 0, "relaxation": 0, "euphoria": 0, "sleep": 0, "good vibes": 0,
                                     "focus": 0, "passion": 0, "cbd": 0})

    # if new cannabinoid is added we need to update VtSearchSerializer and to es mapping
    cannabinoids = JSONField(default={"THC": 0, "THCA": 0, "THCV": 0, "CBD": 0, "CBG": 0, "CBN": 0,
                                      "CBC": 0, "CBDA": 0})

    about = models.TextField(_('Description'), null=True, blank=True)
    origins = models.ManyToManyField('self', symmetrical=False, blank=True)

    removed_by = models.CharField(max_length=20, blank=True, null=True)
    removed_date = models.DateTimeField(blank=True, null=True)

    you_may_also_like_exclude = models.BooleanField(default=False)

    # social fields
    social_image = ResizedImageField(max_length=255, blank=True,
                                     help_text='Maximum file size allowed is 10Mb', validators=[validate_image],
                                     quality=75, size=[1024, 1024], upload_to=upload_to)
    meta_desc = models.CharField(max_length=3072, blank=True)
    meta_keywords = models.CharField(max_length=3072, blank=True)

    cup_winner = models.BooleanField(default=False)
    growing_method = models.IntegerField(choices=GROWING_METHOD_CHOICES, blank=True, null=True)
    lighting = models.IntegerField(choices=LIGHTING_CHOICES, blank=True, null=True)
    nutrient_base = models.IntegerField(choices=NUTRIENT_BASE_CHOICES, blank=True, null=True)

    class Meta:
        unique_together = (("name", "category"),)

    def save(self, *args, **kwargs):
        if self.pk is None and not self.vt_slug:
            self.vt_slug = slugify(self.name)
        super(Vt, self).save(*args, **kwargs)

    @property
    def variety_image(self):
        return static('images/variety-{variety}.png'.format(variety=self.variety))

    @property
    def url(self):
        return self.get_absolute_url()

    def to_search_criteria(self):
        return {
            'vt_types': 'skipped',
            'effects': self.build_criteria_effects(self.effects),
            'benefits': self.build_criteria_effects(self.benefits),
            'side_effects': self.build_criteria_effects(self.side_effects)
        }

    def build_criteria_effects(self, effects_object):
        effects = []
        json = loads(dumps(effects_object))
        for key in json:
            value = json[key]
            if value > 0:
                effects.append({'name': key, 'value': value})
        return effects

    def get_absolute_url(self):
        return reverse('search:vt_detail', kwargs={'vt_variety': self.variety, 'slug_name': self.vt_slug})

    def __str__(self):
        return '{0} - {1}'.format(self.name, self.category)

    @property
    def is_indoor(self):
        return self.growing_method in (self.INDOOR_SOIL, self.INDOOR_HYDRO, self.INDOOR_COCO)

    @property
    def is_clean(self):
        return self.nutrient_base == self.ORGANIC


def upload_image_to(instance, filename):
    return 'vts/{0}/images/{1}___{2}'.format(instance.vt.id, uuid4(), filename)


def validate_image(field_file_obj):
    try:
        file_size = field_file_obj.file.size
        megabyte_limit = settings.MAX_VT_IMAGE_SIZE
        if file_size > megabyte_limit:
            raise ValidationError("Max file size is %sMB" % str(megabyte_limit))
    except OSError:
        raise ValidationError('Image does not exists')


@python_2_unicode_compatible
class VtImage(models.Model):
    vt = models.ForeignKey(Vt, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(max_length=255, upload_to=upload_image_to,
                              help_text='Maximum file size allowed is 10Mb',
                              validators=[validate_image])

    created_date = models.DateField(blank=False, null=False, default=datetime.now)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    is_approved = models.BooleanField(default=False)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        i = self.image
        return '{}: {}'.format(self.vt, i.url if i and i.url else '')

    class Meta:
        ordering = ('created_date',)


@python_2_unicode_compatible
class Effect(models.Model):
    class Meta:
        unique_together = (("effect_type", "data_name"),)

    EFFECT_TYPE_CHOICES = (
        ('effect', 'Effect'),
        ('benefit', 'Benefit'),
        ('side_effect', 'Side Effect'),
    )

    effect_type = models.CharField(max_length=20, choices=EFFECT_TYPE_CHOICES)
    data_name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=100)

    def __str__(self):
        return '{0} - {1}'.format(self.effect_type, self.display_name)


def upload_flavor_image_to(instance, filename):
    return 'flavors/images/{0}___{1}'.format(instance.data_name, filename)


def validate_flavor_image(field_file_obj):
    file_size = field_file_obj.file.size
    one_megabyte = 1 * 1024 * 1024
    if file_size > one_megabyte:
        raise ValidationError("Max file size is %sMB" % str(1))


@python_2_unicode_compatible
class Flavor(models.Model):
    data_name = models.SlugField(max_length=100, help_text='This will be slugified automatically from Display Name')
    display_name = models.CharField(max_length=100)
    image = models.ImageField(max_length=255, upload_to=upload_flavor_image_to, blank=True,
                              help_text='Maximum file size allowed is 1Mb',
                              validators=[validate_flavor_image])

    def save(self, *args, **kwargs):
        if self.pk is None and not self.data_name:
            self.data_name = slugify(self.display_name)
        super(Flavor, self).save(*args, **kwargs)

    def __str__(self):
        return '{0} ({1})'.format(self.data_name, self.display_name)


@python_2_unicode_compatible
class UserSearch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    varieties = JSONField(max_length=250)
    effects = JSONField(max_length=1000)
    benefits = JSONField(max_length=1000)
    side_effects = JSONField(max_length=1000)

    last_modified_date = models.DateTimeField(auto_now=True)

    objects = UserSearchQuerySet.as_manager()

    class Meta:
        ordering = ('-last_modified_date',)

    def to_search_criteria(self):
        return {
            'vt_types': self.varieties,
            'effects': self.effects,
            'benefits': self.benefits,
            'side_effects': self.side_effects
        }

    def __str__(self):
        return '{0} - {1}'.format(self.user, self.last_modified_date)


@python_2_unicode_compatible
class VtReview(ReviewAbstract):
    """
    A 5-star rating
    """
    vt = models.ForeignKey(Vt, on_delete=models.CASCADE)


@python_2_unicode_compatible
class VtRating(models.Model):
    """
    A user's vt review, that user left via Disagree link in SPD
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processed', 'Processed'),
    )

    vt = models.ForeignKey(Vt, on_delete=models.CASCADE)

    effects = JSONField(default={})
    effects_changed = models.BooleanField(default=False)

    benefits = JSONField(default={})
    benefits_changed = models.BooleanField(default=False)

    side_effects = JSONField(default={})
    side_effects_changed = models.BooleanField(default=False)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    removed_date = models.DateTimeField(null=True)

    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='+')
    created_by_ip = models.CharField(max_length=30, blank=True, null=True)
    last_modified_date = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='+')
    last_modified_by_ip = models.CharField(max_length=30, blank=True, null=True)


@python_2_unicode_compatible
class UserFavoriteVt(models.Model):
    vt = models.ForeignKey(Vt, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_date = models.DateTimeField(auto_now=True)
