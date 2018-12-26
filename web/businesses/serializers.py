from rest_framework import serializers

from web.businesses.models import Business, BusinessLocation, BusinessLocationMenuItem


class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ('id', 'name', 'created_date')


class MenuItemSerializer(serializers.ModelSerializer):
    business_location_id = serializers.ReadOnlyField(source='business_location.id')
    location = serializers.SerializerMethodField()
    dispensary = serializers.ReadOnlyField(source='business_location.dispensary')
    delivery = serializers.ReadOnlyField(source='business_location.delivery')
    grow_house = serializers.ReadOnlyField(source='business_location.grow_house')
    delivery_radius = serializers.ReadOnlyField(source='business_location.delivery_radius')
    removed_date = serializers.ReadOnlyField(source='business_location.removed_date')

    class Meta:
        model = BusinessLocationMenuItem
        fields = ('price_gram', 'price_eighth', 'price_quarter', 'price_half', 'in_stock',
                  'business_location_id', 'dispensary', 'delivery', 'grow_house',
                  'delivery_radius', 'location', 'removed_date')

    def get_location(self, instance):
        if instance.business_location.lat and instance.business_location.lng:
            return {'lat': instance.business_location.lat, 'lon': instance.business_location.lng}
        return {'lat': 0, 'lon': 0}


class BusinessLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessLocation
        fields = ('id', 'location_name', 'manager_name', 'location_email', 'image', 'primary', 'dispensary',
                  'delivery', 'street1', 'city', 'state', 'zip_code', 'phone', 'ext', 'timezone', 'about',
                  'delivery_radius', 'mon_open', 'mon_close', 'tue_open', 'tue_close', 'wed_open', 'wed_close',
                  'thu_open', 'thu_close', 'fri_open', 'fri_close', 'sat_open', 'sat_close', 'sun_open', 'sun_close',
                  'lat', 'lng', 'location_raw', 'slug_name', 'city_slug', 'image', 'url', 'urls', 'image_url',
                  'grow_house', 'grow_details')

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
    grow_details = serializers.DictField()
