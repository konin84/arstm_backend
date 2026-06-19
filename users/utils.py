
# users/utils.py
import logging
import secrets
import string
from concurrent.futures import ThreadPoolExecutor

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)
_email_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix='email')


def _send_email_safely(email_message):
    try:
        email_message.send(fail_silently=False)
    except Exception:
        logger.exception("Échec de l'envoi d'email à %s", email_message.to)


def generate_temp_password(length=12):
    """Génère un mot de passe aléatoire sécurisé avec lettres, chiffres et symboles."""
    alphabet = string.ascii_letters + string.digits + '!@#$%&*'
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
    site_url = settings.SITE_URL.rstrip('/')
    logo_url = site_url + staticfiles_storage.url('users/images/arstm_logo.jpeg')

    html_body = render_to_string('users/emails/welcome_email.html', {
        'subject': subject,
        'full_name': user.get_full_name(),
        'role_label': role_label,
        'email': user.email,
        'temp_password': temp_password,
        'logo_url': logo_url,
    })

    recipient = settings.TEST_EMAIL_RECIPIENT or user.email
    email_message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient],
    )
    email_message.attach_alternative(html_body, 'text/html')

    _email_executor.submit(_send_email_safely, email_message)


def send_newsletter_confirmation_email(email):
    """Envoie un email de confirmation lors de l'abonnement à la newsletter."""
    subject = "Bienvenue dans la newsletter de l'ARSTM"
    text_body = f"""Bonjour,

Merci de vous être abonné(e) à la newsletter de l'Académie Régionale des Sciences et Techniques de la Mer (ARSTM).

Vous recevrez désormais nos actualités, événements et offres directement dans votre boîte mail.

Si vous n'êtes pas à l'origine de cette inscription, vous pouvez ignorer ce message sans crainte.

Cordialement,
L'équipe ARSTM
"""
    site_url = settings.SITE_URL.rstrip('/')
    logo_url = site_url + staticfiles_storage.url('users/images/arstm_logo.jpeg')

    html_body = render_to_string('users/emails/newsletter_subscription.html', {
        'subject': subject,
        'logo_url': logo_url,
    })

    recipient = settings.TEST_EMAIL_RECIPIENT or email
    email_message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient],
    )
    email_message.attach_alternative(html_body, 'text/html')

    _email_executor.submit(_send_email_safely, email_message)


def send_newsletter_unsubscribe_email(email):
    """Envoie un email de confirmation de désabonnement à la newsletter."""
    subject = "Vous êtes désabonné(e) de la newsletter de l'ARSTM"
    text_body = f"""Bonjour,

Nous confirmons votre désabonnement de la newsletter de l'Académie Régionale des Sciences et Techniques de la Mer (ARSTM).

Vous ne recevrez plus nos actualités, événements et offres par email.

Si ce désabonnement n'était pas volontaire, vous pouvez vous réabonner à tout moment depuis notre site.

Cordialement,
L'équipe ARSTM
"""
    site_url = settings.SITE_URL.rstrip('/')
    logo_url = site_url + staticfiles_storage.url('users/images/arstm_logo.jpeg')

    html_body = render_to_string('users/emails/newsletter_unsubscribe.html', {
        'subject': subject,
        'logo_url': logo_url,
    })

    recipient = settings.TEST_EMAIL_RECIPIENT or email
    email_message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient],
    )
    email_message.attach_alternative(html_body, 'text/html')

    _email_executor.submit(_send_email_safely, email_message)