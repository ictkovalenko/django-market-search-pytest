import datetime
import json
import logging
import urllib.parse
import uuid

from boto.s3.bucket import Bucket
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.db.models import Prefetch
from rest_framework import permissions
from rest_framework import status
from rest_framework.exceptions import ValidationError as RestFrameworkValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView, ListAPIView, DestroyAPIView

from web.businesses.api.serializers import UserFavoriteLocationSerializer
from web.businesses.models import UserFavoriteLocation
from web.users.login import pre_login
from web.search.api.serializers import SearchCriteriaSerializer, UserFavoriteVtSerializer
from web.search.models import UserSearch, VtReview, VtImage, UserFavoriteVt
from web.search.services import build_vt_rating
from web.users import validators
from web.users.api.permissions import UserAccountOwner
from web.users.api.serializers import (UserDetailSerializer, UserSignUpSerializer, UserLocationSerializer,
                                       UserSerializer)
from web.users.emails import EmailService
from web.users.models import User, PwResetLink, UserSetting, UserLocation

logger = logging.getLogger(__name__)


def bad_request(error_message):
    return Response({
        'error': error_message
    }, status=status.HTTP_400_BAD_REQUEST)


class UsersView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        email = request.GET.get('email').lower()
        does_exist = User.objects.filter(email__iexact=email).exists()
        return Response({'exist': does_exist}, status=status.HTTP_200_OK)


class UserDetailView(UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated, UserAccountOwner)
    serializer_class = UserDetailSerializer

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        super().perform_update(serializer)

        location_data = self.request.data.get('location', {})
        serializer = UserLocationSerializer(data=location_data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        UserLocation.objects.update_or_create(user_id=self.request.user.id, defaults=data)
        return Response({}, status=status.HTTP_200_OK)


class UserChangePwdView(LoginRequiredMixin, APIView):
    permission_classes = (UserAccountOwner,)

    def post(self, request, user_id):
        user = User.objects.get(pk=user_id)
        current_pwd = request.data.get('curPwd')

        does_match = user.check_password(current_pwd)
        if not does_match:
            return bad_request('Current password you entered does not match our entry')

        pwd = request.data.get('pwd')
        pwd2 = request.data.get('pwd2')
        if pwd and pwd2:
            try:
                validators.validate_pwd(pwd, pwd2)
                user.set_password(pwd)
                user.save()
            except ValidationError as e:
                return bad_request(e.message)

        return Response({}, status=status.HTTP_200_OK)


class UserImageView(LoginRequiredMixin, APIView):
    permission_classes = (UserAccountOwner,)

    def post(self, request, user_id):
        user = User.objects.get(pk=user_id)

        if user.image and user.image.url:
            conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
            bucket = Bucket(conn, settings.AWS_STORAGE_BUCKET_NAME)
            k = Key(bucket=bucket, name=user.image.url.split(bucket.name)[1])
            k.delete()

        file = request.FILES.get('file')
        user.image = file
        user.save()

        return Response({}, status=status.HTTP_200_OK)


class UserSettingsView(LoginRequiredMixin, APIView):
    permission_classes = (UserAccountOwner,)

    def get(self, request, user_id):
        user = User.objects.get(pk=user_id)
        settings_raw = UserSetting.objects.filter(user=user)
        settings = []

        for s in settings_raw:
            settings.append({
                'setting_name': s.setting_name,
                'setting_value': s.setting_value
            })

        return Response(settings, status=status.HTTP_200_OK)

    def post(self, request, user_id):
        setting_name = request.data.get('setting_name')
        setting_value = request.data.get('setting_value')
        user = User.objects.get(pk=user_id)

        try:
            setting = UserSetting.objects.get(setting_name=setting_name, user=user)
        except UserSetting.DoesNotExist:
            setting = UserSetting(setting_name=setting_name, user=user)

        setting.setting_value = setting_value
        setting.save()

        return Response({}, status=status.HTTP_200_OK)


class UserLoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        email = request.data.get('email').lower()
        pwd = request.data.get('password')

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return bad_request('Email or password does not match')

        does_match = user.check_password(pwd)
        if not does_match:
            return bad_request('Email or password does not match')

        authenticated = authenticate(username=user.email, password=pwd)
        if authenticated is None:
            return bad_request('Email or password does not match')

        if not UserSetting.objects.filter(user=user).exists():
            UserSetting.create_for_user(user,
                                        json.loads(urllib.parse.unquote(request.COOKIES.get('user_settings', '[]')))
                                        )

        pre_login(user, request)
        login(request, authenticated)
        return Response({'user': UserSerializer(user).data}, status=status.HTTP_200_OK)


class UserSignUpWizardView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        request_data = request.data
        location_data = request.data.get('location')
        search_criteria = request.data.get('search_criteria')

        user_serializer = UserSignUpSerializer(data=request_data)
        location_serializer = UserLocationSerializer(data=location_data)

        try:
            user_serializer.is_valid(raise_exception=True)
            location_serializer.is_valid(raise_exception=True)
        except RestFrameworkValidationError as e:
            return bad_request(e.detail)

        user_data = user_serializer.validated_data
        l_data = location_serializer.validated_data
        email = user_data.get('email').lower()

        try:
            user = user_serializer.save()
            location = UserLocation(user=user, street1=l_data.get('street1'), city=l_data.get('city'),
                                    state=l_data.get('state'), zipcode=l_data.get('zipcode'),
                                    lat=l_data.get('lat'), lng=l_data.get('lng'),
                                    location_raw=l_data.get('location_raw'))
            location.save()

            if search_criteria:
                types, effects, benefits, side_effects = SearchCriteriaSerializer(
                    data=search_criteria).get_search_criteria()
                if types and effects and benefits and side_effects:
                    UserSearch.objects.create(user=user, varieties=types, effects=effects,
                                              benefits=benefits, side_effects=side_effects)
        except Exception:
            logger.exception('Cannot sign up user')

            if UserLocation.objects.filter(user__email__iexact=email).exists():
                l = UserLocation.objects.get(user__email__iexact=email)
                l.delete()

            UserSearch.objects.filter(user__email__iexact=email).delete()

            if User.objects.filter(email__iexact=email).exists():
                u = User.objects.get(email__iexact=email)
                u.delete()

            return bad_request('Something gone wrong. Please, try again.')

        authenticated = authenticate(username=user.email, password=user_data.get('pwd'))
        if authenticated is None:
            return bad_request('Cannot authenticate user')

        login(request, authenticated)

        try:
            EmailService().send_confirmation_email(user)
        except Exception:
            logger.exception('Cannot send an email to {0}'.format(user.email))

        return Response({'user': UserSerializer(user).data}, status=status.HTTP_200_OK)


class ResendConfirmationEmailView(LoginRequiredMixin, APIView):
    def get(self, request):
        authenticated_user = request.user
        EmailService().send_confirmation_email(authenticated_user)
        return Response({}, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        user_id = request.GET.get('uid')
        token = request.GET.get('t')

        if not user_id or not token:
            return bad_request('Cannot validate your token. Please, try to reset you password one more time.')

        try:
            user = User.objects.get(pk=int(user_id))
        except User.DoesNotExist:
            return bad_request('There is no user to reset password for.')

        try:
            link = PwResetLink.objects.get(user=user)
        except PwResetLink.DoesNotExist:
            return bad_request('Cannot validate this reset link. Please, try to reset you password one more time.')

        if link.token != token:
            return bad_request('This link is invalid. Please, try to reset you password one more time.')

        now = datetime.datetime.now()
        delta = now - link.last_modified_date.replace(tzinfo=None)

        if delta.days >= 2:
            return bad_request('This link is inactive. Please, try to reset you password one more time.')

        return Response({}, status=status.HTTP_200_OK)

    def post(self, request):
        action = request.data.get('action')

        if action == 'send-reset-email':
            return self.process_send_reset_email_action(request)

        if action == 'reset-pwd':
            return self.process_reset_pwd_action(request)

        return bad_request('Cannot determine required action.')

    def process_send_reset_email_action(self, request):
        email = request.data.get('email').lower()

        if not email:
            return bad_request('Email is required')

        try:
            validator = EmailValidator()
            validator.__call__(email)
        except ValidationError:
            return bad_request('Invalid email format')

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            user = None

        if user is None:
            return bad_request('There is no account registered for this email')

        try:
            link = PwResetLink.objects.get(user=user)
        except PwResetLink.DoesNotExist:
            link = PwResetLink()

        token = '{0}-{1}'.format(uuid.uuid4(), uuid.uuid4())
        link.user = user
        link.token = token
        link.last_modified_date = datetime.datetime.now()
        link.save()

        EmailService().send_reset_pwd_email(user, token)

        return Response({}, status=status.HTTP_200_OK)

    def process_reset_pwd_action(self, request):
        user_id = request.data.get('uid')
        token = request.data.get('t')
        pwd = request.data.get('pwd')
        pwd2 = request.data.get('pwd2')

        if not user_id or not token:
            return bad_request('Cannot validate your token. Please, try to reset you password one more time.')

        try:
            user = User.objects.get(pk=int(user_id))
        except User.DoesNotExist:
            return bad_request('There is no user to reset password for.')

        try:
            link = PwResetLink.objects.get(user=user)
        except PwResetLink.DoesNotExist:
            return bad_request('Cannot validate this reset link. Please, try to reset you password one more time.')

        if link.token != token:
            return bad_request('This link is invalid. Please, try to reset you password one more time.')

        now = datetime.datetime.now()
        delta = now - link.last_modified_date.replace(tzinfo=None)

        if delta.days >= 2:
            return bad_request('This link is inactive. Please, try to reset you password one more time.')
        try:
            validators.validate_pwd(pwd, pwd2)
        except ValidationError as e:
            return bad_request(e.message)

        user.set_password(pwd)
        user.save()

        return Response({}, status=status.HTTP_200_OK)


class UserVtSearchesView(LoginRequiredMixin, APIView):
    permission_classes = (UserAccountOwner,)

    def get(self, request, user_id):
        user_search = UserSearch.objects.user_criteria(request.user)
        if user_search:
            return Response({'vt_search': user_search}, status=status.HTTP_200_OK)
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def post(self, request, user_id):
        search_criteria = request.data.get('search_criteria')
        types, effects, benefits, side_effects = SearchCriteriaSerializer(data=search_criteria).get_search_criteria()

        UserSearch.objects.create(
            user=request.user, varieties=types, effects=effects, benefits=benefits, side_effects=side_effects
        )
        if not request.user.display_search_history:
            request.user.display_search_history = True
            request.user.save()
        return Response({}, status=status.HTTP_200_OK)

    def delete(self, request, user_id):
        request.user.display_search_history = False
        request.user.save()
        return Response({}, status=status.HTTP_200_OK)


class VtRatingView(LoginRequiredMixin, APIView):
    permission_classes = (UserAccountOwner,)

    def get(self, request, user_id):
        raw = VtReview.objects.filter(created_by__id=user_id).order_by('-created_date')
        ratings = []
        for r in raw:
            images = VtImage.objects.filter(vt=r.vt)
            ratings.append({
                'id': r.id,
                'vt_id': r.vt.id,
                'vt_name': r.vt.name,
                'vt_slug': r.vt.vt_slug,
                'vt_variety': r.vt.variety,
                'vt_image': images[0] if len(images) > 0 else None,
                'vt_overall_rating': build_vt_rating(r.vt),
                'rating': r.rating,
                'review': r.review,
                'created_date': r.created_date
            })
        return Response({'reviews': ratings}, status=status.HTTP_200_OK)


class UserFavoritesView(LoginRequiredMixin, ListAPIView):
    permission_classes = (permissions.IsAuthenticated, UserAccountOwner)
    serializer_class = UserFavoriteVtSerializer
    location_serializer_class = UserFavoriteLocationSerializer

    def get_serializer_class(self):
        if self.kwargs['favorite_type'] in ('dispensary', 'delivery'):
            return self.location_serializer_class
        return super().get_serializer_class()

    def get_queryset(self):
        if 'vt' == self.kwargs['favorite_type']:
            return UserFavoriteVt.objects \
                .filter(created_by__id=self.kwargs['user_id'])\
                .prefetch_related(
                    Prefetch('vt__images',
                             queryset=VtImage.objects.filter(is_approved=True), to_attr='vt_images'))\
                .order_by('-created_date')
        if 'dispensary' == self.kwargs['favorite_type']:
            return UserFavoriteLocation.objects\
                .get_user_favorites(self.kwargs['user_id']) \
                .filter(location__dispensary=True)
        if 'delivery' == self.kwargs['favorite_type']:
            return UserFavoriteLocation.objects\
                .get_user_favorites(self.kwargs['user_id']) \
                .filter(location__delivery=True)
        return UserFavoriteVt.objects.none()


class UserFavoritesDeleteView(LoginRequiredMixin, DestroyAPIView):
    permission_classes = (permissions.IsAuthenticated, UserAccountOwner)
    lookup_url_kwarg = 'favorite_id'

    def get_queryset(self):
        if 'vt' == self.kwargs['favorite_type']:
            return UserFavoriteVt.objects.filter(created_by__id=self.kwargs['user_id'])
        return UserFavoriteLocation.objects.get_user_favorites(self.kwargs['user_id'])


class UserGeoLocationView(LoginRequiredMixin, APIView):
    permission_classes = (UserAccountOwner,)

    def get(self, request, user_id):
        if UserLocation.objects.filter(user__id=user_id).exists():
            location = UserLocation.objects.get(user__id=user_id)
            return Response({'location': UserLocationSerializer(location).data}, status=status.HTTP_200_OK)

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def post(self, request, user_id):
        serializer = UserLocationSerializer(data=request.data.get('address'))
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            location = UserLocation.objects.get(user__id=user_id)
            location.street1 = data.get('street1')
            location.city = data.get('city')
            location.state = data.get('state')
            location.zipcode = data.get('zipcode')
            location.lat = data.get('lat')
            location.lng = data.get('lng')
            location.location_raw = data.get('location_raw') if data.get('location_raw') else {}
        except UserLocation.DoesNotExist:
            location = UserLocation(
                user=request.user,
                street1=data.get('street1'), city=data.get('city'),
                state=data.get('state'), zipcode=data.get('zipcode'),
                lat=data.get('lat'), lng=data.get('lng'),
                location_raw=data.get('location_raw') if data.get('location_raw') else {}
            )

        location.save()

        if request.data.get('timezone'):
            user = User.objects.get(pk=request.user.id)
            user.timezone = request.data.get('timezone')
            user.save()

        return Response({}, status=status.HTTP_200_OK)


class UserProximityView(LoginRequiredMixin, APIView):
    permission_classes = (UserAccountOwner,)

    def post(self, request, user_id):
        user = User.objects.get(pk=user_id)
        user.proximity = request.data.get('proximity')
        user.save()
        return Response({}, status=status.HTTP_200_OK)
