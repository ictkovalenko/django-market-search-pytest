import uuid
from datetime import datetime
from random import shuffle

import pytz
from django.core.exceptions import ValidationError
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.db.models import Avg

from web.businesses.models import BusinessLocation, Business, LocationReview
from web.system.models import SystemProperty
from web.users import validators
from web.users.models import User, UserLocation


class BusinessSignUpService:
    def enroll_new_business(self, data):
        user = self.validate_and_create_user(data)
        business = self.validate_and_create_business(data, user)
        self.create_business_locations(data, business)
        return business

    def validate_and_create_user(self, data):
        does_exist = User.objects.filter(email=data.get('email')).exists()
        if does_exist:
            raise ValidationError('There is already an account associated with that email address')

        validators.validate_pwd(data.get('pwd'), data.get('pwd2'))

        if not data.get('is_terms_accepted'):
            raise ValidationError('Agreement is required')

        if not data.get('certified_legal_compliance'):
            raise ValidationError('Certification is required')

        verify_automatically = SystemProperty.objects.get(name='auto_email_verification_for_business')

        user = User(
            email=data.get('email'),
            username=str(uuid.uuid4())[:30],
            is_age_verified=True,
            is_email_verified=verify_automatically and verify_automatically.value == 'true',
            type='business'
        )
        user.set_password(data.get('pwd'))
        user.save()

        location = UserLocation(user=user, street1=data.get('street1'), city=data.get('city'),
                                state=data.get('state'), zipcode=data.get('zip_code'),
                                lat=data.get('lat'), lng=data.get('lng'), location_raw=data.get('location_raw'))
        location.save()

        return user

    def validate_and_create_business(self, data, user):
        if not data.get('delivery') and not data.get('dispensary') and not data.get('grow_house'):
            raise ValidationError('Business type is required')

        if not data.get('certified_legal_compliance'):
            raise ValidationError('Certification is required')

        business = Business(
            name=data.get('name'),
            certified_legal_compliance=data.get('certified_legal_compliance'),
            created_by=user
        )
        business.save()

        business.users.add(user)
        business.save()

        return business

    def create_business_locations(self, data, business):
        location = self.build_business_location(data, business)
        location.primary = True
        location.dispensary = data.get('dispensary')
        location.delivery = data.get('delivery')
        location.save()

    def build_business_location(self, data, business):
        business_location = BusinessLocation(
            business=business,
            location_name=business.name,
            location_email=business.created_by.email,
            dispensary=data.get('dispensary'),
            delivery=data.get('delivery'),
            delivery_radius=data.get('delivery_radius'),
            grow_house=data.get('grow_house'),
            street1=data.get('street1'),
            city=data.get('city'),
            state=data.get('state'),
            zip_code=data.get('zip_code'),
            phone=data.get('phone'),
            lat=data.get('lat'),
            lng=data.get('lng'),
            location_raw=data.get('location_raw'),
            mon_open=data.get('mon_open'),
            mon_close=data.get('mon_close'),
            tue_open=data.get('tue_open'),
            tue_close=data.get('tue_close'),
            wed_open=data.get('wed_open'),
            wed_close=data.get('wed_close'),
            thu_open=data.get('thu_open'),
            thu_close=data.get('thu_close'),
            fri_open=data.get('fri_open'),
            fri_close=data.get('fri_close'),
            sat_open=data.get('sat_open'),
            sat_close=data.get('sat_close'),
            sun_open=data.get('sun_open'),
            sun_close=data.get('sun_close')
        )
        return business_location


class BusinessLocationService:
    def create_location(self, business_id, location):
        business = Business.objects.get(pk=business_id)
        is_primary_exist = BusinessLocation.objects.filter(business__id=business_id, primary=True,
                                                           removed_date=None).exists()
        l = BusinessLocation(
            business=business,
            primary=not is_primary_exist,
            location_name=location.get('location_name'),
            location_email=location.get('location_email'),
            street1=location.get('street1'),
            city=location.get('city'),
            state=location.get('state'),
            zip_code=location.get('zip_code'),
            phone=location.get('phone'),
            delivery=location.get('delivery'),
            dispensary=location.get('dispensary'),
            delivery_radius=location.get('delivery_radius'),
            grow_house=location.get('grow_house'),
            grow_details=location.get('grow_details', {}),
            lat=location.get('lat'),
            lng=location.get('lng'),
            location_raw=location.get('location_raw') if location.get('location_raw') else {},
            timezone=location.get('timezone'),
            about=location.get('about')
        )
        l.save()
        return l

    def update_location(self, business_location_id, location):
        l = BusinessLocation.objects.get(pk=business_location_id)
        l.location_name = location.get('location_name')
        l.location_email = location.get('location_email')
        l.street1 = location.get('street1')
        l.city = location.get('city')
        l.state = location.get('state')
        l.zip_code = location.get('zip_code')
        l.phone = location.get('phone')
        l.delivery = location.get('delivery')
        l.dispensary = location.get('dispensary')
        l.grow_house = location.get('grow_house')
        l.grow_details = location.get('grow_details', {})
        l.delivery_radius = location.get('delivery_radius')
        l.lat = location.get('lat') if location.get('lat') else l.lat
        l.lng = location.get('lng') if location.get('lng') else l.lng
        l.location_raw = location.get('location_raw') if location.get('location_raw') else l.location_raw
        l.timezone = location.get('timezone')
        l.about = location.get('about')
        l.save()
        return l

    def remove_location(self, business_location_id, current_user_id):
        l = BusinessLocation.objects.get(pk=business_location_id)
        l.removed_by = current_user_id
        l.removed_date = datetime.now()
        l.save()

        if l.primary:
            locations = BusinessLocation.objects.filter(business__id=l.business.id, removed_date=None).order_by('id')
            if len(locations) > 0:
                new_primary = locations[0]
                new_primary.primary = True
                new_primary.save()


def get_location_rating(location_id):
    rating = LocationReview.objects.filter(location__id=location_id).aggregate(avg_rating=Avg('rating'))
    rating = rating.get('avg_rating')
    return 'Not Rated' if rating is None else "{0:.2f}".format(round(rating, 2))


def get_open_closed(location_json, time_format='%H:%M:%S'):
    days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

    timezone_str = location_json.get('timezone')
    if timezone_str is None:
        return ''

    location_tz = pytz.timezone(timezone_str)

    now = datetime.now(tz=location_tz)
    weekday = days[now.weekday()]

    open_str = location_json.get('{0}_open'.format(weekday))
    close_str = location_json.get('{0}_close'.format(weekday))

    if open_str is None or close_str is None:
        return ''

    def seconds(time):
        return 3600*time.hour + 60*time.minute + time.second

    time_now = seconds(now.time())
    open_time = seconds(datetime.strptime(open_str, time_format).time())
    close_time = seconds(datetime.strptime(close_str, time_format).time())

    if time_now < open_time or time_now > close_time:
        return 'Closed Now'

    if time_now > (close_time - 1800):
        return 'Closing Soon'

    return 'Opened'


class FeaturedBusinessLocationService:
    def __get_featured_by_zip(self, qs, **kwargs):
        zip_code = kwargs.get('zip_code')

        if zip_code is not None:
            return qs.filter(featured__zip_code=zip_code)

        return []

    def __get_featured_by_distance(self, qs, **kwargs):
        longitude = kwargs.get('longitude')
        latitude = kwargs.get('latitude')

        if longitude is not None and latitude is not None:
            qs = qs.filter(featured__isnull=False)
            qs = qs.filter(geo_location__distance_lt=(Point(longitude, latitude), Distance(mi=8)))
            return qs

        return []

    def __get_by_distance(self, qs, **kwargs):
        longitude = kwargs.get('longitude')
        latitude = kwargs.get('latitude')

        if longitude is not None and latitude is not None:
            return qs.distance(Point(longitude, latitude))\
                     .order_by('distance')[:100]

        return []

    def __get_random(self, qs, **kwargs):
        # TODO: This is a full table scan & order which is unacceptable
        # for anything more than a small table
        return qs.order_by('?')[:kwargs.get('result_len')]

    pipeline = (__get_featured_by_zip,
                __get_featured_by_distance,
                __get_by_distance,
                __get_random,
                )

    def get_list(self, zip_code=None, longitude=None, latitude=None, result_len=3):
        base_qs = BusinessLocation.objects.filter(removed_date__isnull=True, dispensary=True)
        featured, new_featured = [], []

        for fn in self.pipeline:
            qs = base_qs.exclude(id__in=[x.id for x in featured])

            new_featured = list(fn(self, qs, zip_code=zip_code, longitude=longitude,
                                   latitude=latitude, result_len=result_len))
            shuffle(new_featured)
            featured.extend(new_featured[:result_len - len(featured)])

            if len(featured) == result_len:
                break

        return featured
