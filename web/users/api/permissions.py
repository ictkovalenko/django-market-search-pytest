from rest_framework import permissions


class UserAccountOwner(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.id == int(view.kwargs.get('user_id'))
