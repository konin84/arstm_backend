# apps/users/backends.py
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

User = get_user_model()


class EmailOrPhoneBackend(ModelBackend):
    """
    Authentification par email ou numéro de téléphone.
    Accepte aussi bien username= (Django admin) qu'email= (SimpleJWT avec USERNAME_FIELD='email').
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Quand USERNAME_FIELD='email', SimpleJWT appelle authenticate(email=...) au lieu de authenticate(username=...)
        identifier = username or kwargs.get('email') or kwargs.get('phone')
        if identifier is None:
            return None

        try:
            user = User.objects.get(Q(email=identifier) | Q(phone=identifier))
        except User.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
