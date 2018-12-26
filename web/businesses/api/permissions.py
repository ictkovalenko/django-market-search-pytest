from rest_framework import permissions

from web.businesses.models import Business, BusinessLocation


class BusinessAccountOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            # Allow any GET request but restrict all others (POST, PUT, DELETE)
            return True

        business_id = view.kwargs.get('business_id')
        filterargs = {'users__id': request.user.id, 'pk': business_id}
        return Business.objects.filter(**filterargs).exists()


class BusinessLocationAccountOwnerOrStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_staff:
            return True

        if request.method == 'GET':
            # Allow any GET request but restrict all others (POST, PUT, DELETE)
            return True

        business_id = view.kwargs.get('business_id')
        business_location_id = view.kwargs.get('business_location_id')

        permission_kwargs = {
            'business_id': business_id,
            'business__users__id': request.user.id,
        }

        # By convention PUT 0 means create, so check business only
        try:
            if int(business_location_id) != 0:
                permission_kwargs['id'] = business_location_id
        except ValueError:
            permission_kwargs['id'] = business_location_id

        return BusinessLocation.objects.filter(
            business_id=business_id,
            business__users__id=request.user.id,
        ).exists()


class AllowAnyGetOperation(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            # Allow any GET request but restrict all others (POST, PUT, DELETE)
            return True

        return request.user.is_authenticated()
