from rest_framework import serializers

from web.businesses.models import phone_number_validator, LocationReview, GrowerDispensaryPartnership, \
    BusinessLocationMenuItem, UserFavoriteLocation
from web.search.api.services import VtDetailsService


class BusinessSignUpSerializer(serializers.Serializer):
    name = serializers.CharField()
    dispensary = serializers.BooleanField()
    delivery = serializers.BooleanField()
    delivery_radius = serializers.FloatField(required=False)
    grow_house = serializers.BooleanField()
    certified_legal_compliance = serializers.BooleanField()
    is_terms_accepted = serializers.BooleanField()

    email = serializers.CharField()
    pwd = serializers.CharField()
    pwd2 = serializers.CharField()

    street1 = serializers.CharField()
    city = serializers.CharField()
    state = serializers.CharField()
    zip_code = serializers.CharField()
    phone = serializers.CharField()

    lat = serializers.FloatField(allow_null=True)
    lng = serializers.FloatField(allow_null=True)
    location_raw = serializers.JSONField()

    mon_open = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True, required=False)
    mon_close = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True, required=False)
    tue_open = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True, required=False)
    tue_close = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True, required=False)
    wed_open = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True, required=False)
    wed_close = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True, required=False)
    thu_open = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True, required=False)
    thu_close = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True, required=False)
    fri_open = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True, required=False)
    fri_close = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True, required=False)
    sat_open = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True, required=False)
    sat_close = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True, required=False)
    sun_open = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True, required=False)
    sun_close = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True, required=False)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class BusinessLocationDetailSerializer(serializers.Serializer):
    location_name = serializers.CharField()
    image_url = serializers.CharField(read_only=True)
    manager_name = serializers.CharField(allow_blank=True, allow_null=True)
    location_email = serializers.CharField()
    url = serializers.CharField(read_only=True)
    urls = serializers.DictField(read_only=True)

    formatted_address = serializers.CharField(read_only=True)
    phone = serializers.CharField(validators=[phone_number_validator])
    ext = serializers.CharField(allow_blank=True, allow_null=True)
    timezone = serializers.CharField(allow_blank=True, allow_null=True)

    about = serializers.CharField(allow_blank=True)

    dispensary = serializers.BooleanField()
    delivery = serializers.BooleanField()
    grow_house = serializers.BooleanField()
    grow_details = serializers.DictField()

    delivery_radius = serializers.FloatField(allow_null=True)

    lat = serializers.FloatField(allow_null=True)
    lng = serializers.FloatField(allow_null=True)
    location_raw = serializers.JSONField(default={})

    mon_open = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True)
    mon_close = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True)
    tue_open = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True)
    tue_close = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True)
    wed_open = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True)
    wed_close = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True)
    thu_open = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True)
    thu_close = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True)
    fri_open = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True)
    fri_close = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True)
    sat_open = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True)
    sat_close = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True)
    sun_open = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True)
    sun_close = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True)

    def update(self, inst, data):
        inst.location_name = data.get('location_name')
        inst.manager_name = data.get('manager_name')
        inst.location_email = data.get('location_email')
        inst.dispensary = data.get('dispensary')
        inst.delivery = data.get('delivery')
        inst.delivery_radius = data.get('delivery_radius')
        inst.grow_house = data.get('grow_house')
        inst.grow_details = data.get('grow_details', {})
        inst.phone = data.get('phone')
        inst.ext = data.get('ext')
        inst.timezone = data.get('timezone')
        inst.about = data.get('about')
        inst.lat = data.get('lat') if data.get('lat') else inst.lat
        inst.lng = data.get('lng') if data.get('lng') else inst.lng
        inst.location_raw = data.get('location_raw') if data.get('location_raw') else inst.location_raw
        inst.mon_open = data.get('mon_open')
        inst.mon_close = data.get('mon_close')
        inst.tue_open = data.get('tue_open')
        inst.tue_close = data.get('tue_close')
        inst.wed_open = data.get('wed_open')
        inst.wed_close = data.get('wed_close')
        inst.thu_open = data.get('thu_open')
        inst.thu_close = data.get('thu_close')
        inst.fri_open = data.get('fri_open')
        inst.fri_close = data.get('fri_close')
        inst.sat_open = data.get('sat_open')
        inst.sat_close = data.get('sat_close')
        inst.sun_open = data.get('sun_open')
        inst.sun_close = data.get('sun_close')
        inst.save()

    def create(self, validated_data):
        pass


class BusinessLocationMenuItemListSerializer(serializers.ListSerializer):

    def to_representation(self, data):
        ret = super().to_representation(data)
        request = self.context['view'].request

        if request.GET.get('ddp') and request.user.is_authenticated():
            vt_ids = [mi.get('vt_id') for mi in ret]

            scores = VtDetailsService().calculate_srx_scores(vt_ids, request.user)
            if len(scores) > 0:
                for mi in ret:
                    mi['match_score'] = scores.get(mi.get('vt_id'))
        return ret


class BusinessLocationMenuItemSerializer(serializers.ModelSerializer):
    vt_id = serializers.IntegerField(required=False)
    url = serializers.ReadOnlyField(source='vt.get_absolute_url')
    vt_name = serializers.ReadOnlyField(source='vt.name')
    vt_variety = serializers.ReadOnlyField(source='vt.variety')
    report_count = serializers.ReadOnlyField(required=False)

    class Meta:
        model = BusinessLocationMenuItem
        list_serializer_class = BusinessLocationMenuItemListSerializer
        fields = ('id', 'vt_id', 'vt_name', 'vt_variety', 'price_gram',
                  'price_eighth', 'price_quarter', 'price_half', 'in_stock', 'url', 'report_count')

    def __init__(self, instance=None, **kwargs):
        if instance and kwargs.get('data') and kwargs['data'].get('menu_item'):
            kwargs['data'] = kwargs['data']['menu_item']
        super().__init__(instance, **kwargs)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if not self.instance and not attrs.get('vt_id'):
            raise serializers.ValidationError({'vt_id': 'This field is required.'})
        return attrs


class LocationReviewFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationReview
        fields = ('rating', 'review')


class GrowerDispensaryPartnershipSerializer(serializers.ModelSerializer):
    dispensary = BusinessLocationDetailSerializer(required=False)
    dispensary_id = serializers.IntegerField(allow_null=False)
    grower = BusinessLocationDetailSerializer(required=False)
    grower_id = serializers.IntegerField(allow_null=False)

    class Meta:
        model = GrowerDispensaryPartnership
        fields = ('id', 'dispensary', 'dispensary_id', 'grower', 'grower_id')


class UserFavoriteLocationSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='location.location_name')
    image = serializers.SerializerMethodField()
    street1 = serializers.ReadOnlyField(source='location.street1')
    city = serializers.ReadOnlyField(source='location.city')
    state = serializers.ReadOnlyField(source='location.state')
    zip_code = serializers.ReadOnlyField(source='location.zip_code')
    phone = serializers.ReadOnlyField(source='location.phone')
    email = serializers.ReadOnlyField(source='location.location_email')
    url = serializers.ReadOnlyField(source='location.get_absolute_url')

    class Meta:
        model = UserFavoriteLocation
        fields = ('id', 'name', 'image', 'street1', 'city', 'state', 'zip_code',
                  'phone', 'email', 'created_date', 'url')

    def get_image(self, instance):
        if instance.location.image:
            return instance.location.image.url
