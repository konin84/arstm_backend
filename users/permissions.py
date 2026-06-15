from rest_framework import permissions

PRIVILEGED_ROLES = ('admin', 'moderator')


class IsAdminOrModerator(permissions.BasePermission):
    """Grants access to admins (is_staff) and moderators."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in PRIVILEGED_ROLES
        )
