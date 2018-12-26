from web.search.api.serializers import VtDetailSerializer, VtRatingSerializer
from web.search.es_service import SearchElasticService
from web.search.models import UserSearch, Vt, VtImage, VtReview, VtRating, UserFavoriteVt
from web.search.services import build_vt_rating


class VtDetailsService:
    def build_vt_details(self, vt_id, current_user=None):
        vt = Vt.objects.get(pk=vt_id)
        image = VtImage.objects.filter(vt=vt, is_approved=True).first()
        vt_origins = self.get_vt_origins(vt)
        rating = build_vt_rating(vt)
        reviews = self.get_vt_reviews(vt)

        if current_user:
            vt_srx_score = self.calculate_srx_score(vt, current_user)
            vt_review = VtRating.objects.filter(vt=vt, created_by=current_user, removed_date=None)
            favorite = UserFavoriteVt.objects.filter(vt=vt, created_by=current_user).exists()
            is_rated = VtReview.objects.filter(vt=vt, created_by=current_user).exists()
            user_criteria = UserSearch.objects.user_criteria(current_user)
            if user_criteria:
                user_criteria = user_criteria.to_search_criteria()
        else:
            vt_srx_score = 0
            vt_review = []
            favorite = None
            is_rated = None
            user_criteria = None

        return {
            'vt': VtDetailSerializer(vt).data,
            'vt_image': image.image.url if image and image.image else None,
            'vt_origins': vt_origins,
            'vt_rating': rating,
            'user_vt_review': VtRatingSerializer(vt_review[0]).data if len(vt_review) > 0 else None,
            'user_criteria': user_criteria,
            'vt_reviews': reviews,
            'vt_srx_score': vt_srx_score,
            'favorite': favorite,
            'is_rated': is_rated,
            'lighting': vt.get_lighting_display(),
            'is_clean': vt.is_clean,
            'nutrient_base': vt.get_nutrient_base_display(),
            'is_indoor': vt.is_indoor,
            'growing_method': vt.get_growing_method_display(),
            'cup_winner': vt.cup_winner
        }

    @staticmethod
    def get_vt_origins(current_vt):
        vt_origins = []
        for o in current_vt.origins.all()[:5]:
            vt_origins.append(VtDetailSerializer(o).data)
        return vt_origins

    @staticmethod
    def get_also_like_vts(current_vt, current_user=None):
        latest_user_search = UserSearch.objects.user_criteria(current_user)

        also_like_vts = []

        if latest_user_search:
            data = SearchElasticService().query_vt_srx_score(latest_user_search.to_search_criteria(), 2000, 0,
                                                                 include_locations=False, is_similar=True,
                                                                 similar_vt_id=current_vt.id)
            for index, s in enumerate(data.get('list')):
                also_like_vts.append(s)

        if len(also_like_vts) == 0:
            criteria = current_vt.to_search_criteria()
            if len(criteria['effects']) > 0 or len(criteria['benefits']) > 0 or len(criteria['side_effects']) > 0:
                criteria['vt_types'] = 'skipped'
                data = SearchElasticService().query_vt_srx_score(criteria, 2000, 0,
                                                                     include_locations=False, is_similar=True,
                                                                     similar_vt_id=current_vt.id)
                for s in data.get('list'):
                    also_like_vts.append(s)

        return also_like_vts

    @staticmethod
    def calculate_srx_score(current_vt, current_user):
        latest_user_search = UserSearch.objects.user_criteria(current_user)

        if latest_user_search:
            if VtRating.objects.filter(vt=current_vt, created_by=current_user,
                                           removed_date=None).exists():
                score = SearchElasticService().query_user_review_srx_score(latest_user_search.to_search_criteria(),
                                                                           vt_id=current_vt.id,
                                                                           user_id=current_user.id)
                return score
            else:
                data = SearchElasticService().query_vt_srx_score(
                    latest_user_search.to_search_criteria(), vt_ids=[current_vt.id], include_locations=False)
                vt = data.get('list')[0] if len(data.get('list')) > 0 else {'match_percentage': 0}
                return vt.get('match_percentage')

        return 0

    @staticmethod
    def calculate_srx_scores(vt_ids, current_user):
        latest_user_search = UserSearch.objects.user_criteria(current_user)

        if latest_user_search:
            data = SearchElasticService().query_vt_srx_score(latest_user_search.to_search_criteria(),
                                                                 vt_ids=vt_ids, result_filter='all')
            scores = {}
            vts = data.get('list')

            for s in vts:
                scores[s.get('id')] = s.get('match_percentage')

            return scores

        return []

    def get_vt_reviews(self, current_vt):
        reviews_raw = VtReview.objects.filter(vt=current_vt,
                                                  review_approved=True).order_by('-created_date')[:3]
        reviews = []
        for r in reviews_raw:
            reviews.append(self.build_review(r))
        return reviews

    def get_all_approved_vt_reviews(self, vt_id):
        reviews_raw = VtReview.objects.filter(vt__id=vt_id,
                                                  review_approved=True).order_by('-created_date')
        reviews = []
        for r in reviews_raw:
            reviews.append(self.build_review(r))
        return reviews

    @staticmethod
    def build_review(review):
        return {
            'id': review.id,
            'rating': review.rating,
            'review': review.review,
            'created_date': review.created_date,
            'created_by_name': review.username,
            'created_by_image': review.created_by.image.url
            if review.created_by.image and review.created_by.image.url else None
        }

    @staticmethod
    def build_vt_locations(vt_id, current_user, order_field=None, order_dir=None, location_type=None):
        service = SearchElasticService()
        es_response = service.get_locations(vt_id=vt_id, current_user=current_user,
                                            order_field=order_field, order_dir=order_dir, location_type=location_type,
                                            size=6, only_active=True)

        locations = service.transform_location_results(es_response, vt_id=vt_id)
        return {'locations': locations}
