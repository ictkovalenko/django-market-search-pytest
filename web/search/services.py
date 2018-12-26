from django.contrib.staticfiles.templatetags.staticfiles import static
from django.db.models import Avg, Prefetch
from web.search.models import Vt, VtImage, VtReview


def build_vt_rating(vt):
    rating = VtReview.objects.filter(vt=vt).aggregate(avg_rating=Avg('rating'))
    rating = rating.get('avg_rating')
    return 'Not Rated' if rating is None else "{0:.2f}".format(round(rating, 2))


def get_vts_and_images_for_location(location):
    urls = []
    vts = Vt.objects.filter(menu_items__business_location=location).order_by('name')
    vts = Vt.prefetch_related(Prefetch('images', queryset=VtImage.objects.filter(is_approved=True)))

    for vt in vts:
        images = list(vt.images.all())
        if images:
            for image in images:
                if image.is_primary:
                    url = image.image.url
                    break
            else:
                url = images[0].image.url
        else:
            url = static('images/weed_small.jpg')

        urls.append(url)

    return list(zip(vts, urls))
