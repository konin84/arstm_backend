import email.policy
import logging
import secrets
import string
from concurrent.futures import ThreadPoolExecutor

from django.conf import settings
from django.contrib.staticfiles.finders import find as find_static
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)
_email_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix='email')

LOGO_STATIC_PATH = 'users/images/arstm_logo.jpeg'
LOGO_CID = 'arstm_logo'


class _RelatedEmailMessage(EmailMultiAlternatives):
    """
    EmailMultiAlternatives ne propose plus de façon publique d'embarquer une image
    inline (cid:) depuis Django 6.0 (l'attribut `mixed_subtype` a été supprimé).
    On suit donc le pattern documenté de la lib standard `email` : appeler
    `add_related()` directement sur la partie HTML pour la transformer en
    multipart/related contenant le HTML + l'image.
    """

    def __init__(self, *args, inline_images=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.inline_images = inline_images or []  # [(cid, data, mimetype), ...]

    def message(self, *, policy=email.policy.default):
        msg = super().message(policy=policy)
        if self.inline_images and self.alternatives:
            html_part = msg.get_payload()[-1]
            for cid, data, mimetype in self.inline_images:
                maintype, subtype = mimetype.split('/', 1)
                html_part.add_related(data, maintype, subtype, cid=f'<{cid}>')
        return msg


def _send_email_safely(email_message):
    """Exécuté dans le pool de threads : log l'erreur au lieu de la laisser disparaître silencieusement."""
    try:
        email_message.send(fail_silently=False)
    except Exception:
        logger.exception("Échec de l'envoi d'email à %s", email_message.to)


def _load_logo():
    """Renvoie (data, mimetype) du logo ARSTM, ou None s'il est introuvable."""
    logo_path = find_static(LOGO_STATIC_PATH)
    if not logo_path:
        logger.warning("Logo ARSTM introuvable (%s) : email envoyé sans logo.", LOGO_STATIC_PATH)
        return None
    with open(logo_path, 'rb') as f:
        return f.read(), 'image/jpeg'


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
    """Envoie les identifiants de connexion au nouvel utilisateur, avec le logo ARSTM dans l'email."""
    role_label = dict(user.ROLE_CHOICES).get(user.role, user.role)
    subject = "Bienvenue sur la plateforme ARSTM — Vos identifiants de connexion"
    text_body = f"""Bonjour {user.get_full_name()},

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
    html_body = render_to_string('users/emails/welcome_email.html', {
        'subject': subject,
        'full_name': user.get_full_name(),
        'role_label': role_label,
        'email': user.email,
        'temp_password': temp_password,
        'logo_cid': LOGO_CID,
    })

    logo = _load_logo()
    inline_images = [(LOGO_CID, logo[0], logo[1])] if logo else []

    recipient = settings.TEST_EMAIL_RECIPIENT or user.email
    email_message = _RelatedEmailMessage(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient],
        inline_images=inline_images,
    )
    email_message.attach_alternative(html_body, 'text/html')

    _email_executor.submit(_send_email_safely, email_message)
