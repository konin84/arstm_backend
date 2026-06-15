import secrets
import string
from django.core.mail import send_mail
from django.conf import settings


def generate_temp_password(length=12):
    """Génère un mot de passe aléatoire sécurisé avec lettres, chiffres et symboles."""
    alphabet = string.ascii_letters + string.digits + '!@#$%&*'
    # On s'assure d'avoir au moins un caractère de chaque catégorie
    password = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
        secrets.choice('!@#$%&*'),
    ]
    password += [secrets.choice(alphabet) for _ in range(length - 4)]
    secrets.SystemRandom().shuffle(password)
    return ''.join(password)


def send_welcome_email(user, temp_password):
    """Envoie les identifiants de connexion au nouvel utilisateur."""
    role_label = dict(user.ROLE_CHOICES).get(user.role, user.role)
    subject = "Bienvenue sur la plateforme ARSTM — Vos identifiants de connexion"
    message = f"""Bonjour {user.get_full_name()},

Votre compte a été créé sur la plateforme de l'ARSTM avec le profil : {role_label}.

─────────────────────────────
  Identifiant : {user.email}
  Mot de passe temporaire : {temp_password}
─────────────────────────────

Veuillez vous connecter et changer votre mot de passe dès votre première connexion.
Ce mot de passe est temporaire et ne sera plus valide après modification.

Cordialement,
L'équipe ARSTM
"""
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
