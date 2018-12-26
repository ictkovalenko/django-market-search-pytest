import json
import logging
from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import permissions
from rest_framework import status
from rest_framework.generics import get_object_or_404, CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from web.common.text import obfuscate
from web.search.api.serializers import SearchCriteriaSerializer, VtReviewFormSerializer, VtImageSerializer, \
    VtSearchSerializer
from web.search.api.services import VtDetailsService
from web.search.es_service import SearchElasticService
from web.search.models import Vt, VtImage, Effect, VtReview, VtRating, UserFavoriteVt, \
    Flavor
from web.search.vt_es_service import VtESService
from web.search.vt_user_rating_es_service import VtUserRatingESService
from web.system.models import SystemProperty

logger = logging.getLogger(__name__)


def bad_request(error_message):
    return Response({
        'error': error_message
    }, status=status.HTTP_400_BAD_REQUEST)


class VtSearchWizardView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        types, effects, benefits, side_effects = SearchCriteriaSerializer(
            data=request.data.get('search_criteria')).get_search_criteria()

        request.session['search_criteria'] = {
            'vt_types': types,
            'effects': effects,
            'benefits': benefits,
            'side_effects': side_effects
        }

        return Response({}, status=status.HTTP_200_OK)


class VtSearchResultsView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        result_filter = request.GET.get('filter')
        page = request.GET.get('page', 1)
        size = request.GET.get('size', 25)
        start_from = (int(page) - 1) * int(size)

        search_criteria = request.session.get('search_criteria')

        if not search_criteria:
            return Response({
                "error": "Cannot determine a search criteria."
            }, status=status.HTTP_400_BAD_REQUEST)

        data = SearchElasticService().query_vt_srx_score(search_criteria, size, start_from,
                                                             current_user=request.user,
                                                             result_filter=result_filter)
        result_list = data.get('list')

        if not (request.user.is_authenticated() and request.user.is_email_verified):
            result_list = [dict(x, name=obfuscate(x['name']), vt_slug=obfuscate(x['vt_slug']))
                           for x in result_list]

        return Response({
            'search_results': result_list,
            'search_results_total': data.get('total')
        }, status=status.HTTP_200_OK)


class VtFavoriteView(LoginRequiredMixin, APIView):
    def post(self, request, vt_id):
        add_to_favorites = request.data.get('like')
        favorite_vt = UserFavoriteVt.objects.filter(vt__id=vt_id, created_by=request.user)

        if add_to_favorites and len(favorite_vt) == 0:
            favorite_vt = UserFavoriteVt(
                vt=Vt.objects.get(id=vt_id),
                created_by=request.user
            )
            favorite_vt.save()
        elif len(favorite_vt) > 0:
            favorite_vt[0].delete()

        return Response({}, status=status.HTTP_200_OK)


class VtSRXScoreView(LoginRequiredMixin, APIView):
    def get(self, request, vt_id):
        vt = get_object_or_404(Vt, pk=vt_id)
        score = VtDetailsService().calculate_srx_score(vt, request.user)
        return Response({'srx_score': score}, status=status.HTTP_200_OK)


class VtAlsoLikeView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, vt_id):
        vt = Vt.objects.get(pk=vt_id)
        user = request.user
        also_like_vts = VtDetailsService().get_also_like_vts(vt,
                                                                         user if user.is_authenticated() else None)
        return Response({'also_like_vts': also_like_vts}, status=status.HTTP_200_OK)


class VtLookupView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        query = request.GET.get('q')
        result = SearchElasticService().lookup_vt(query)
        return Response({
            'total': result.get('total'),
            'payloads': result.get('payloads')
        }, status=status.HTTP_200_OK)


class VtImagesView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, vt_id):
        images = VtImage.objects.filter(is_approved=True, vt=vt_id).order_by('-is_primary')
        serializer = VtImageSerializer(images, many=True)
        return Response({'images': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request, vt_id):
        if not request.user.is_authenticated():
            return Response({}, status=status.HTTP_401_UNAUTHORIZED)

        file = request.FILES.get('file')
        vt = Vt.objects.get(pk=vt_id)
        image = VtImage(image=file, vt=vt, created_by=request.user)
        image.save()
        return Response({}, status=status.HTTP_200_OK)


class VtRateView(CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = VtReviewFormSerializer

    def perform_create(self, serializer):
        serializer.save(
            vt=get_object_or_404(Vt, pk=self.kwargs.get('vt_id')),
            created_by=self.request.user,
            review_approved=False if serializer.validated_data.get('review') else True
        )


class VtDetailsView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, vt_id):
        user = request.user
        details = VtDetailsService().build_vt_details(vt_id, user if user.is_authenticated() else None)
        return Response(details, status=status.HTTP_200_OK)


class VtDeliveriesView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, vt_id):
        d = request.GET
        order_field = d.get('order_field')
        order_dir = d.get('order_dir')
        location_type = d.get('filter')
        user = request.user

        l = VtDetailsService().build_vt_locations(vt_id, user, order_field,
                                                          order_dir, location_type)
        return Response(l, status=status.HTTP_200_OK)


class VtReviewsView(LoginRequiredMixin, APIView):
    def get(self, request, vt_id):
        reviews = VtDetailsService().get_all_approved_vt_reviews(vt_id)
        return Response({'reviews': reviews}, status=status.HTTP_200_OK)


class VtRatingsView(LoginRequiredMixin, APIView):
    def post(self, request, vt_id):
        data = request.data
        effect_type = data.get('type')
        effects = data.get('effects')
        vt = Vt.objects.get(id=vt_id)
        sender_ip = get_client_ip(request)

        if VtRating.objects.filter(vt=vt, created_by=request.user, removed_date=None).exists():
            r = VtRating.objects.get(vt=vt, created_by=request.user, removed_date=None)
        else:
            r = VtRating(vt=vt, effects=vt.effects, benefits=vt.benefits,
                             side_effects=vt.side_effects, created_by=request.user,
                             created_by_ip=sender_ip)

        if 'effects' == effect_type:
            r.effects = self.build_effects_object(effects, vt.effects)
            r.effects_changed = True
            r.last_modified_by = request.user
            r.last_modified_by_ip = sender_ip
            r.save()
            self.recalculate_global_effects(request, vt)

        if 'benefits' == effect_type:
            r.benefits = self.build_effects_object(effects, vt.benefits)
            r.benefits_changed = True
            r.last_modified_by = request.user
            r.last_modified_by_ip = sender_ip
            r.save()
            self.recalculate_global_effects(request, vt)

        if 'side_effects' == effect_type:
            r.side_effects = self.build_effects_object(effects, vt.side_effects)
            r.side_effects_changed = True
            r.last_modified_by = request.user
            r.last_modified_by_ip = sender_ip
            r.save()
            self.recalculate_global_effects(request, vt)

        VtUserRatingESService().save_vt_review(r, vt.id, request.user.id)

        return Response({}, status=status.HTTP_200_OK)

    def build_effects_object(self, effects, vt_default_effects):
        for default_e in vt_default_effects:
            vt_default_effects[default_e] = 0

        effects_to_persist = vt_default_effects
        for e in effects:
            effects_to_persist[e.get('name')] = e.get('value')
        return effects_to_persist

    def recalculate_global_effects(self, request, vt, immediate=False):
        try:
            recalculate_size = int(SystemProperty.objects.get(name='rating_recalculation_size').value)
        except SystemProperty.DoesNotExist:
            recalculate_size = 10

        ratings = VtRating.objects.filter(vt=vt, status='pending', removed_date=None)

        # First check if there are "recalculate_size" new ratings
        if (len(ratings) >= recalculate_size) or immediate:
            sender_ip = get_client_ip(request)

            for r in ratings:
                r.status = 'processed'
                r.last_modified_ip = sender_ip
                r.last_modified_by = request.user
                r.save()

            # Recalculate Global scores for each review in the system that wasn't removed
            ratings = VtRating.objects.filter(vt=vt, removed_date=None)

            vt.effects = self.calculate_new_global_values(ratings, 'effects')
            vt.benefits = self.calculate_new_global_values(ratings, 'benefits')
            vt.side_effects = self.calculate_new_global_values(ratings, 'side_effects')
            vt.save()

            VtESService().save_vt(vt)

    def calculate_new_global_values(self, reviews, effect_type):
        total_vt_effects = {}

        if effect_type == 'effects':
            for r in reviews:
                for effect_name in r.effects:
                    if total_vt_effects.get(effect_name):
                        total_vt_effects[effect_name] += r.effects[effect_name]
                    else:
                        total_vt_effects[effect_name] = r.effects[effect_name]

        if effect_type == 'benefits':
            for r in reviews:
                for effect_name in r.benefits:
                    if total_vt_effects.get(effect_name):
                        total_vt_effects[effect_name] += r.benefits[effect_name]
                    else:
                        total_vt_effects[effect_name] = r.benefits[effect_name]

        if effect_type == 'side_effects':
            for r in reviews:
                for effect_name in r.side_effects:
                    if total_vt_effects.get(effect_name):
                        total_vt_effects[effect_name] += r.side_effects[effect_name]
                    else:
                        total_vt_effects[effect_name] = r.side_effects[effect_name]

        for effect_name in total_vt_effects:
            total_vt_effects[effect_name] /= len(reviews)

        return total_vt_effects

    def delete(self, request, vt_id):
        effect_type = request.data.get('effect_type')
        sender_ip = get_client_ip(request)
        vt = Vt.objects.get(id=vt_id)
        rating = VtRating.objects.get(vt=vt, created_by=request.user, removed_date=None)

        if effect_type == 'effects':
            rating.effects = vt.effects
            rating.effects_changed = False

        if effect_type == 'benefits':
            rating.benefits = vt.benefits
            rating.benefits_changed = False

        if effect_type == 'side_effects':
            rating.side_effects = vt.side_effects
            rating.side_effects_changed = False

        if not rating.effects_changed and not rating.benefits_changed and not rating.side_effects_changed:
            rating.removed_date = datetime.now()

        rating.last_modified_ip = sender_ip
        rating.last_modified_by = request.user
        rating.save()

        VtUserRatingESService().save_vt_review(rating, vt.id, request.user.id)

        if rating.status == 'processed':
            self.recalculate_global_effects(request, vt, immediate=True)

        return Response({}, status=status.HTTP_200_OK)


def get_client_ip(request):
    if request.META.get('HTTP_X_FORWARDED_FOR'):
        return request.META.get('HTTP_X_FORWARDED_FOR').split(',')[-1].strip()
    elif request.META.get('HTTP_X_REAL_IP'):
        return request.META.get('HTTP_X_REAL_IP')
    else:
        return request.META.get('REMOTE_ADDR')


class VtEffectView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, effect_type):
        effects_raw = Effect.objects.filter(effect_type=effect_type)
        effects = []

        for e in effects_raw:
            effects.append({
                'data_name': e.data_name,
                'display_name': e.display_name
            })

        return Response(effects, status=status.HTTP_200_OK)


class VtFlavorView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        flavors_raw = Flavor.objects.all()
        flavors = []

        for e in flavors_raw:
            flavors.append({
                'data_name': e.data_name,
                'display_name': e.display_name,
                'image': e.image.url if e.image else None
            })

        return Response(flavors, status=status.HTTP_200_OK)


class VtsListByVarietyView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, vt_variety):
        limit = request.GET.get('limit')
        vts = []
        if limit:
            vts_raw = Vt.objects.filter(variety=vt_variety).order_by('id')[:int(limit)]
        else:
            vts_raw = Vt.objects.filter(variety=vt_variety).order_by('id')

        for e in vts_raw:
            images = VtImage.objects.filter(vt=e)
            vts.append({
                'image': images[0].image.url if len(images) > 0 and images[0].image else None,
                'name': e.name,
                'variety': e.variety,
                'slug': e.vt_slug
            })

        return Response(vts, status=status.HTTP_200_OK)


class BusinessLocationLookupView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, bus_type):
        query = request.GET.get('q')
        location = json.loads(request.GET.get('loc')) if request.GET.get('loc') else None
        tz = request.GET.get('tz')
        result = SearchElasticService().lookup_business_location(query, bus_type=[bus_type],
                                                                 location=location, timezone=tz)

        return Response({
            'total': result.get('total'),
            'payloads': result.get('payloads')
        }, status=status.HTTP_200_OK)


class VtSearchAPIView(APIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = VtSearchSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.GET)
        serializer.is_valid(raise_exception=True)
        query = serializer.data
        current_user = request.user
        q = query.get('q')
        if q:
            result = SearchElasticService().lookup_vt_by_name(
                q, current_user, size=query['size'], start_from=query.get('start_from', 0))
        else:
            result = SearchElasticService().advanced_search(
                query, current_user, size=query['size'], start_from=query.get('start_from', 0))

        if not (request.user.is_authenticated() and request.user.is_email_verified):
            result['list'] = [dict(x, name=obfuscate(x['name'] or ''), vt_slug=obfuscate(x['vt_slug'] or ''))
                              for x in result['list']]
        return Response(result, status=status.HTTP_200_OK)
