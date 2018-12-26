import logging
import uuid

import datetime
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError as DjangoValidationError

from web.system.models import SystemProperty
from web.users import validators
from web.users.models import User, UserLocation, GENDER

logger = logging.getLogger(__name__)


class UserLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLocation
        fields = ('street1', 'city', 'state', 'zipcode', 'lat', 'lng', 'location_raw')


class UserSerializer(serializers.ModelSerializer):
    geo_location = UserLocationSerializer(read_only=True, allow_null=True)

    class Meta:
        model = User
        exclude = ('password',)


class UserDetailSerializer(serializers.ModelSerializer):
    MONTH_CHOICES = [(datetime.date(1900, i, 1).strftime('%b'),
                      datetime.date(1900, i, 1).strftime('%B')) for i in range(1, 13)]
    DAY_CHOICES = list(zip(range(1, 32), range(1, 32)))
    YEAR_CHOICES = list(zip(range(1900, datetime.date.today().year),
                            range(1900, datetime.date.today().year)))
    GENDER_CHOICES = GENDER

    birth_month = serializers.ChoiceField(choices=MONTH_CHOICES, label='', required=False, allow_blank=True,
                                          allow_null=True, style={'template_pack': 'rest_framework/inline/'})
    birth_day = serializers.ChoiceField(choices=DAY_CHOICES, label='', required=False, allow_null=True,
                                        allow_blank=True, style={'template_pack': 'rest_framework/inline/'})
    birth_year = serializers.ChoiceField(choices=YEAR_CHOICES, label='', required=False, allow_null=True,
                                         allow_blank=True, style={'template_pack': 'rest_framework/inline/'})
    gender = serializers.ChoiceField(choices=GENDER_CHOICES, label='', required=False,
                                     allow_null=True, allow_blank=True)

    style = {}

    class Meta:
        model = User
        fields = ('name', 'first_name', 'last_name', 'email', 'birth_month', 'birth_day', 'birth_year', 'gender',
                  'timezone')
        extra_kwargs = {
            'email': {'label': 'Email', 'required': True, 'allow_blank': False, 'allow_null': False},
            'name': {'label': 'Username'}
        }

    def __init__(self, instance=None, **kwargs):
        super().__init__(instance, **kwargs)
        if instance and instance.name:
            self.fields['name'].read_only = True

    def validate(self, attrs):
        attrs = super().validate(attrs)

        try:
            validators.validate_name(attrs.get('name'), self.instance.pk)
        except DjangoValidationError as e:
            raise ValidationError({'name': e.messages})

        if User.objects.filter(email__iexact=attrs['email']).exclude(pk=self.instance.pk).exists():
            raise ValidationError({'email': ['There is already an account associated with that email address']})

        if attrs.get('birth_month') or attrs.get('birth_day') or attrs.get('birth_year'):
            if not attrs.get('birth_month'):
                raise ValidationError({'birth_month': ['This field is required.']})
            if not attrs.get('birth_day'):
                raise ValidationError({'birth_day': ['This field is required.']})
            if not attrs.get('birth_year'):
                raise ValidationError({'birth_year': ['This field is required.']})

        attrs['birth_month'] = attrs.get('birth_month') or None
        attrs['birth_day'] = attrs.get('birth_day') or None
        attrs['birth_year'] = attrs.get('birth_year') or None

        return attrs


class UserSignUpSerializer(serializers.ModelSerializer):
    pwd = serializers.CharField()
    pwd2 = serializers.CharField()
    is_terms_accepted = serializers.BooleanField()

    class Meta:
        model = User
        fields = ('name', 'first_name', 'last_name', 'is_age_verified', 'email', 'pwd', 'pwd2', 'is_terms_accepted')
        extra_kwargs = {
            'name': {'required': True},
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate(self, attrs):
        attrs = super().validate(attrs)

        if not attrs.get('is_terms_accepted'):
            raise ValidationError({'is_terms_accepted': ['This field is required.']})
        if not attrs.get('is_age_verified'):
            raise ValidationError({'is_age_verified': ['This field is required.']})

        attrs['email'] = attrs['email'].lower()
        if User.objects.filter(email__iexact=attrs['email']).exists():
            raise ValidationError({'email': ['There is already an account associated with that email address']})

        try:
            validators.validate_pwd(attrs.get('pwd'), attrs.get('pwd2'))
        except DjangoValidationError as e:
            raise ValidationError({'pwd': e.messages, 'pwd2': e.messages})

        try:
            validators.validate_name(attrs.get('name'), None)
        except DjangoValidationError as e:
            raise ValidationError({'name': e.messages})
        return attrs

    def save(self, **kwargs):
        proximity = SystemProperty.objects.max_delivery_radius()

        user = User(
            name=self.validated_data.get('name'),
            first_name=self.validated_data.get('first_name'),
            last_name=self.validated_data.get('last_name'),
            email=self.validated_data.get('email').lower(),
            username=str(uuid.uuid4())[:30],
            is_age_verified=self.validated_data.get('is_age_verified'),
            is_email_verified=False,
            proximity=proximity,
            type='consumer'
        )
        user.set_password(self.validated_data.get('pwd'))
        user.save()
        return user
