from rest_framework import serializers


class BusinessLocationESSerializer(serializers.Serializer):
    business_id = serializers.IntegerField()
    business_location_id = serializers.IntegerField(source='id')
    url = serializers.CharField()
    urls = serializers.DictField()
    image = serializers.CharField(source='image_url')
    location_name = serializers.CharField()
    slug_name = serializers.CharField()
    manager_name = serializers.CharField()
    location_email = serializers.CharField()
    dispensary = serializers.BooleanField()
    delivery = serializers.BooleanField()
    grow_house = serializers.BooleanField()
    delivery_radius = serializers.FloatField()
    street1 = serializers.CharField()
    city = serializers.CharField()
    state = serializers.CharField()
    zip_code = serializers.CharField()
    lat = serializers.FloatField()
    lng = serializers.FloatField()
    location_raw = serializers.CharField()
    phone = serializers.CharField()
    ext = serializers.CharField()
    timezone = serializers.CharField()
    removed_by_id = serializers.CharField(source='removed_by')
    removed_date = serializers.DateTimeField()
    created_date = serializers.DateTimeField()
    mon_open = serializers.TimeField(format='%H:%M:%S', input_formats=['%H:%M:%S'], allow_null=True)
    mon_close = serializers.TimeField(format='%H:%M:%S', input_formats=['%H:%M:%S'], allow_null=True)
    tue_open = serializers.TimeField(format='%H:%M:%S', input_formats=['%H:%M:%S'], allow_null=True)
    tue_close = serializers.TimeField(format='%H:%M:%S', input_formats=['%H:%M:%S'], allow_null=True)
    wed_open = serializers.TimeField(format='%H:%M:%S', input_formats=['%H:%M:%S'], allow_null=True)
    wed_close = serializers.TimeField(format='%H:%M:%S', input_formats=['%H:%M:%S'], allow_null=True)
    thu_open = serializers.TimeField(format='%H:%M:%S', input_formats=['%H:%M:%S'], allow_null=True)
    thu_close = serializers.TimeField(format='%H:%M:%S', input_formats=['%H:%M:%S'], allow_null=True)
    fri_open = serializers.TimeField(format='%H:%M:%S', input_formats=['%H:%M:%S'], allow_null=True)
    fri_close = serializers.TimeField(format='%H:%M:%S', input_formats=['%H:%M:%S'], allow_null=True)
    sat_open = serializers.TimeField(format='%H:%M:%S', input_formats=['%H:%M:%S'], allow_null=True)
    sat_close = serializers.TimeField(format='%H:%M:%S', input_formats=['%H:%M:%S'], allow_null=True)
    sun_open = serializers.TimeField(format='%H:%M:%S', input_formats=['%H:%M:%S'], allow_null=True)
    sun_close = serializers.TimeField(format='%H:%M:%S', input_formats=['%H:%M:%S'], allow_null=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class MenuItemESSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    vt_id = serializers.IntegerField()
    vt_name = serializers.SerializerMethodField()
    price_gram = serializers.FloatField()
    price_eighth = serializers.FloatField()
    price_quarter = serializers.FloatField()
    price_half = serializers.FloatField()
    in_stock = serializers.BooleanField()
    removed_date = serializers.DateTimeField()

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    def get_vt_name(self, obj):
        return obj.vt.name
