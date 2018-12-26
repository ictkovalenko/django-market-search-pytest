from web.businesses.models import Business, BusinessLocation
from web.businesses.serializers import BusinessSerializer


def pre_login(user, request):
    # If user is a business user we need a business object to be available across the app
    if user.type == 'business':
        business = Business.objects.filter(users__in=[user]).first()
        if not business:
            return

        request.session['business'] = BusinessSerializer(business).data

        locations = BusinessLocation.objects.filter(business__id=business.id, primary=True, removed_date=None)
        if len(locations) > 0:
            primary = locations[0]
            business_image = primary.image.url if len(
                locations) > 0 and primary.image and primary.image.url else None
            request.session['business_image'] = business_image
