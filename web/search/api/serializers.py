from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from web.search.es_script_score import advanced_search_sort, advanced_search_nested_location_filter
from web.search.models import Vt, VtReview, VtRating, VtImage, UserFavoriteVt
from web.search.services import build_vt_rating


class SearchCriteriaSerializer(serializers.Serializer):
    step1 = serializers.DictField()
    step2 = serializers.DictField()
    step3 = serializers.DictField()
    step4 = serializers.DictField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def get_search_criteria(self):
        self.is_valid()

        step_1_data = self.validated_data.get('step1', {})
        step_2_data = self.validated_data.get('step2', {})
        step_3_data = self.validated_data.get('step3', {})
        step_4_data = self.validated_data.get('step4', {})

        types = 'skipped' if step_1_data.get('skipped') else step_1_data
        effects = 'skipped' if step_2_data.get('skipped') else step_2_data.get('effects', {})
        benefits = 'skipped' if step_3_data.get('skipped') else step_3_data.get('effects', {})
        side_effects = 'skipped' if step_4_data.get('skipped') else step_4_data.get('effects', {})
        return types, effects, benefits, side_effects


class VtDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vt
        fields = ('name', 'vt_slug', 'variety', 'category',
                  'effects', 'benefits', 'side_effects', 'flavor', 'about', 'variety_image')


class VtRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = VtRating
        fields = ('effects', 'effects_changed', 'benefits', 'benefits_changed', 'side_effects', 'side_effects_changed',
                  'status')


class VtReviewFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = VtReview
        fields = ('rating', 'review')


class VtImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VtImage


class VtSearchSerializer(serializers.ModelSerializer):

    BEST_MATCH, LOCATION, NAME, PRICE = '', 'location', 'name', 'price'
    MAX_PRICE_GRAM, PRICE_EIGHTH, MAX_PRICE_EIGHTH, PRICE_QUARTER, MAX_PRICE_QUARTER = \
        'max_price_gram', 'price_eighth', 'max_price_eighth', 'price_quarter', 'max_price_quarter'

    SORT_CHOICES = (
        (BEST_MATCH, 'best match'),
        (LOCATION, 'location'),
        (NAME, 'name'),
        (PRICE, 'price'),
    )
    SORT_OPTIONS = [key for key, value in SORT_CHOICES]

    SORT_FIELDS = {
        BEST_MATCH: lambda **kwargs: '_score',
        PRICE: lambda **kwargs: {
            'locations.price_gram': advanced_search_sort(**kwargs)
        },
        LOCATION: lambda **kwargs: {
            '_geo_distance': advanced_search_sort(
                subquery={"unit": "mi", "distance_type": "plane",
                          'locations.location': {"lat": kwargs.get('lat'), "lon": kwargs.get('lon')}},
                **kwargs
            )
        },
        NAME: lambda **kwargs: {'name.raw': {
            "order": 'asc',
            "nested_path": "locations",
            "nested_filter": {"bool": {'must': advanced_search_nested_location_filter()}}
        }},
        MAX_PRICE_GRAM: lambda **kwargs: {
            'locations.price_gram': advanced_search_sort(subquery={"order": 'desc'}, **kwargs)
        },
        PRICE_EIGHTH: lambda **kwargs: {
            'locations.price_eighth': advanced_search_sort(**kwargs)
        },
        MAX_PRICE_EIGHTH: lambda **kwargs: {
            'locations.price_eighth': advanced_search_sort(subquery={"order": 'desc'}, **kwargs)
        },
        PRICE_QUARTER: lambda **kwargs: {
            'locations.price_quarter': advanced_search_sort(**kwargs)
        },
        MAX_PRICE_QUARTER: lambda **kwargs: {
            'locations.price_quarter': advanced_search_sort(subquery={"order": 'desc'}, **kwargs)
        }
    }

    CANNABINOIDS = ['thc', 'thca', 'thcv', 'cbd', 'cbg', 'cbn', 'cbc', 'cbda']
    TERPENES = ['humulene', 'pinene', 'linalool', 'caryophyllene', 'myrcene', 'terpinolene', 'ocimene', 'limonene',
                'camphene', 'terpineol', 'phellandrene', 'carene', 'pulegone', 'sabinene', 'geraniol', 'valencene']
    TERPENES_ABBREVIATION = {
        'humulene': 'H', 'pinene': 'P', 'linalool': 'L', 'caryophyllene': 'Cr', 'myrcene': 'M', 'terpinolene': 'T',
        'ocimene': 'O', 'limonene': 'Le', 'camphene': 'C', 'terpineol': 'Ti', 'phellandrene': 'Ph', 'carene': 'Ce',
        'pulegone': 'Pu', 'sabinene': 'S', 'geraniol': 'G', 'valencene': 'Va'
    }

    q = serializers.CharField(required=False)
    page = serializers.IntegerField(required=False, default=1)
    size = serializers.IntegerField(required=False, default=24, max_value=24)
    start_from = serializers.IntegerField(required=False)
    sort = serializers.MultipleChoiceField(required=False, choices=SORT_CHOICES)

    variety = serializers.MultipleChoiceField(required=False, choices=Vt.VARIETY_CHOICES)
    is_indoor = serializers.BooleanField(default=False, required=False)
    is_clean = serializers.BooleanField(default=False, required=False)
    # cannabinoids
    thc_from = serializers.FloatField(allow_null=True, required=False)
    thc_to = serializers.FloatField(allow_null=True, required=False)
    thca_from = serializers.FloatField(allow_null=True, required=False)
    thca_to = serializers.FloatField(allow_null=True, required=False)
    thcv_from = serializers.FloatField(allow_null=True, required=False)
    thcv_to = serializers.FloatField(allow_null=True, required=False)
    cbd_from = serializers.FloatField(allow_null=True, required=False)
    cbd_to = serializers.FloatField(allow_null=True, required=False)
    cbg_from = serializers.FloatField(allow_null=True, required=False)
    cbg_to = serializers.FloatField(allow_null=True, required=False)
    cbn_from = serializers.FloatField(allow_null=True, required=False)
    cbn_to = serializers.FloatField(allow_null=True, required=False)
    cbc_from = serializers.FloatField(allow_null=True, required=False)
    cbc_to = serializers.FloatField(allow_null=True, required=False)
    cbda_from = serializers.FloatField(allow_null=True, required=False)
    cbda_to = serializers.FloatField(allow_null=True, required=False)

    # terpenes
    humulene = serializers.BooleanField(default=False, required=False)
    pinene = serializers.BooleanField(default=False, required=False)
    linalool = serializers.BooleanField(default=False, required=False)
    caryophyllene = serializers.BooleanField(default=False, required=False)
    myrcene = serializers.BooleanField(default=False, required=False)
    terpinolene = serializers.BooleanField(default=False, required=False)
    ocimene = serializers.BooleanField(default=False, required=False)
    limonene = serializers.BooleanField(default=False, required=False)
    camphene = serializers.BooleanField(default=False, required=False)
    terpineol = serializers.BooleanField(default=False, required=False)
    phellandrene = serializers.BooleanField(default=False, required=False)
    carene = serializers.BooleanField(default=False, required=False)
    pulegone = serializers.BooleanField(default=False, required=False)
    sabinene = serializers.BooleanField(default=False, required=False)
    geraniol = serializers.BooleanField(default=False, required=False)
    valencene = serializers.BooleanField(default=False, required=False)

    default_style = {'template_pack': 'pages/search/vt/inlines/'}
    skip_error_fields = ('thc_from', 'thc_to', 'thca_from', 'thca_to', 'cbc_to', 'page', 'size', 'cbn_to',
                         'thcv_from', 'thcv_to', 'cbd_from', 'cbd_to', 'cbg_from', 'cbg_to', 'cbn_from', 'cbc_from',
                         'cbda_from', 'cbda_to')

    class Meta:
        model = Vt
        fields = ('variety', 'cup_winner', 'is_indoor', 'is_clean', 'thc_from', 'thc_to', 'thca_from', 'thca_to',
                  'thcv_from', 'thcv_to', 'cbd_from', 'cbd_to', 'cbg_from', 'cbg_to', 'cbn_from', 'cbn_to', 'cbc_from',
                  'cbc_to', 'cbda_from', 'cbda_to',
                  'humulene', 'pinene', 'linalool', 'caryophyllene', 'myrcene', 'terpinolene', 'ocimene',
                  'limonene', 'camphene', 'terpineol', 'phellandrene', 'carene', 'pulegone', 'sabinene', 'geraniol',
                  'valencene', 'q', 'page', 'size', 'start_from', 'sort')

    def to_internal_value(self, data):
        try:
            return super().to_internal_value(data)
        except ValidationError as e:
            errors = e.detail
            data = data.copy()
            for field in self.skip_error_fields:
                if errors.pop(field, None):
                    data.pop(field)
            if errors.pop('sort', None):
                sort = data.pop('sort', [])
                data.setlist('sort', [item for item in sort if item in self.SORT_OPTIONS])
            if errors:
                raise ValidationError(errors)
            return super().to_internal_value(data)

    def validate(self, attrs):
        page = attrs.get('page') or self.fields['page'].default
        size = attrs.get('size') or self.fields['size'].default
        attrs['start_from'] = (int(page) - 1) * int(size)
        return attrs

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        data = {key: value for key, value in ret.items() if value is not None}
        data['cannabinoids'] = self.CANNABINOIDS
        data['terpenes'] = self.TERPENES
        return data


class UserFavoriteVtSerializer(serializers.ModelSerializer):
    vt_id = serializers.ReadOnlyField(source='vt.id')
    vt_name = serializers.ReadOnlyField(source='vt.name')
    vt_slug = serializers.ReadOnlyField(source='vt.slug')
    vt_variety = serializers.ReadOnlyField(source='vt.variety')
    vt_image = serializers.SerializerMethodField()
    vt_overall_rating = serializers.SerializerMethodField()

    class Meta:
        model = UserFavoriteVt
        fields = ('id', 'vt_id', 'vt_name', 'vt_slug', 'vt_variety',
                  'vt_image', 'vt_overall_rating', 'created_date')

    def get_vt_image(self, instance):
        vt_images = getattr(instance, 'vt_images', None)
        if vt_images:
            return vt_images[0].image.url

    def get_vt_overall_rating(self, instance):
        return build_vt_rating(instance.vt)
