from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Custom permission to admins.
    """

    def has_permission(self, request, view):

        return request.user.is_staff or request.user.is_superuser


class PromoOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to a promo owner.
    """

    def has_object_permission(self, request, view, obj):

        return request.user == obj.recipient or request.user.is_staff or request.user.is_superuser