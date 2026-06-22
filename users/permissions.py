from rest_framework import permissions

PRIVILEGED_ROLES = ('admin', 'moderator')


class IsAdmin(permissions.BasePermission):
    """Grants access to users with role='admin'."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'admin'
        )


class IsAdminOrModerator(permissions.BasePermission):
    """Grants access to admins and moderators."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in PRIVILEGED_ROLES
        )


class IsCandidate(permissions.BasePermission):
    """Grants access to authenticated users with role='candidate'."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'candidate'
        )


class IsAdminOrModeratorOrReadOnly(permissions.BasePermission):
    """Read-only for everyone; write access restricted to admins and moderators."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or getattr(request.user, 'role', None) in PRIVILEGED_ROLES)
        )
