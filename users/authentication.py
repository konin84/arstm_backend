from django.urls import reverse
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import SAFE_METHODS
from rest_framework_simplejwt.authentication import JWTAuthentication


class PasswordAwareJWTAuthentication(JWTAuthentication):
    """
    Tant que `must_change_password` est vrai, bloque l'accès à toute l'API
    sauf : changer le mot de passe, et consulter (lecture seule) son propre
    profil pour que le frontend puisse afficher l'invite de changement.
    """

    def authenticate(self, request):
        result = super().authenticate(request)
        if result is None:
            return None

        user, validated_token = result
        if user.must_change_password and not self._is_allowed_while_pending(request):
            raise PermissionDenied(
                "Vous devez changer votre mot de passe temporaire avant de continuer."
            )
        return result

    @staticmethod
    def _is_allowed_while_pending(request):
        if request.path == reverse('change_password'):
            return True
        if request.path == reverse('user_profile') and request.method in SAFE_METHODS:
            return True
        return False
