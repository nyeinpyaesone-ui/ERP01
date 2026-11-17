"""Permissions shared by ERP module API viewsets."""

from rest_framework.permissions import SAFE_METHODS, BasePermission


class StaffOrReadOnly(BasePermission):
    """Authenticated users may read; only staff/superusers may mutate records."""

    message = "Staff permission is required to change ERP configuration or inventory."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (user.is_staff or user.is_superuser)
        )
