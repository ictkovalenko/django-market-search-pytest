from rest_framework import serializers
from web.businesses.serializers import MenuItemSerializer
from web.search.models import Vt


class VtESSerializer(serializers.ModelSerializer):
    removed_by_id = serializers.ReadOnlyField(source='removed_by')
    name_suggest = serializers.SerializerMethodField()
    terpenes = serializers.SerializerMethodField()
    cannabinoids = serializers.SerializerMethodField()
    locations = serializers.SerializerMethodField()

    class Meta:
        model = Vt
        fields = ('id', 'name', 'vt_slug', 'variety', 'category',
                  'effects', 'benefits', 'side_effects', 'flavor', 'about',
                  'removed_date', 'removed_by_id', 'you_may_also_like_exclude',
                  'name_suggest', 'terpenes', 'cannabinoids', 'cup_winner',
                  'is_indoor', 'is_clean', 'locations')

    def get_name_suggest(self, instance):
        input_variants = [instance.name]
        name_words = instance.name.split(' ')
        for i, name_word in enumerate(name_words):
            if i < len(name_words) - 1:
                input_variants.append('{0} {1}'.format(name_word, name_words[i + 1]))
            else:
                input_variants.append(name_word)
        return {'input': input_variants, 'weight': 100 - len(input_variants)}

    def get_terpenes(self, instance):
        return instance.terpenes and {key.lower(): value for key, value in instance.terpenes.items()}

    def get_cannabinoids(self, instance):
        return instance.cannabinoids and {key.lower(): value for key, value in instance.cannabinoids.items()}

    def get_locations(self, instance):
        queryset = instance.menu_items\
            .filter(business_location__removed_date__isnull=True)\
            .select_related('business_location')
        return MenuItemSerializer(instance=queryset, many=True).data


class VtReviewESSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    rating = serializers.FloatField()
    review = serializers.CharField(allow_blank=True)
    review_approved = serializers.BooleanField()

    created_date = serializers.DateTimeField()
    last_modified_date = serializers.DateTimeField()
