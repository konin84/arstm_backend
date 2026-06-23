
# users/utils.py
import logging
import secrets
import string
from concurrent.futures import ThreadPoolExecutor
from email.mime.image import MIMEImage

from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from interactions.models import NewsletterSubscription
from django.utils.html import strip_tags
from django.core import signing

logger = logging.getLogger(__name__)
_email_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix='email')

LOGO_STATIC_PATH = 'users/images/arstm_logo.jpeg'
LOGO_CID = 'arstm_logo'


def _make_logo_attachment():
    path = finders.find(LOGO_STATIC_PATH)
    if not path:
        path = settings.STATIC_ROOT / LOGO_STATIC_PATH
    with open(path, 'rb') as f:
        data = f.read()
    img = MIMEImage(data, _subtype='jpeg')
    img.add_header('Content-ID', f'<{LOGO_CID}>')
    img.add_header('Content-Disposition', 'inline', filename='arstm_logo.jpeg')
    return img


def _send_email_safely(email_message):
    try:
        email_message.send(fail_silently=False)
    except Exception:
        logger.exception("Échec de l'envoi d'email à %s", email_message.to)


def generate_otp():
    """Génère un code OTP à 6 chiffres sécurisé."""
    return f"{secrets.randbelow(1000000):06d}"


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
    html_body = render_to_string('users/emails/welcome_email.html', {
        'subject': subject,
        'full_name': user.get_full_name(),
        'role_label': role_label,
        'email': user.email,
        'temp_password': temp_password,
    })

    recipient = settings.TEST_EMAIL_RECIPIENT or user.email
    email_message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient],
    )
    email_message.mixed_subtype = 'related'
    email_message.attach_alternative(html_body, 'text/html')
    email_message.attach(_make_logo_attachment())

    _email_executor.submit(_send_email_safely, email_message)


def send_newsletter_confirmation_email(email):
    subject = "Bienvenue dans la newsletter de l'ARSTM"
    site_url = settings.SITE_URL.rstrip('/')
    token = generate_unsubscribe_token(email)
    unsubscribe_url = f"{site_url}/newsletter/unsubscribe?token={token}"

    text_body = f"""Bonjour,

Merci de vous être abonné(e) à la newsletter de l'ARSTM.

Vous pouvez vous désabonner à tout moment ici : {unsubscribe_url}

Cordialement,
L'équipe ARSTM
"""

    html_body = render_to_string('users/emails/newsletter_subscription.html', {
        'subject': subject,
        'unsubscribe_url': unsubscribe_url,
    })

    recipient = settings.TEST_EMAIL_RECIPIENT or email
    email_message = EmailMultiAlternatives(
        subject=subject, body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL, to=[recipient],
    )
    email_message.mixed_subtype = 'related'
    email_message.attach_alternative(html_body, 'text/html')
    email_message.attach(_make_logo_attachment())
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
    html_body = render_to_string('users/emails/newsletter_unsubscribe.html', {
        'subject': subject,
    })

    recipient = settings.TEST_EMAIL_RECIPIENT or email
    email_message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient],
    )
    email_message.mixed_subtype = 'related'
    email_message.attach_alternative(html_body, 'text/html')
    email_message.attach(_make_logo_attachment())

    _email_executor.submit(_send_email_safely, email_message)


def send_newsletter_broadcast(subject, html_content, text_content=None):
    """
    Diffuse un message à tous les abonnés actifs de la newsletter.
    Retourne le nombre de destinataires ciblés.
    """
    recipients = list(
        NewsletterSubscription.objects.filter(is_active=True)
        .values_list('lead__email', flat=True)
    )
    if not recipients:
        return 0

    def _send_batch():
        for email in recipients:
            message = EmailMultiAlternatives(
                subject=subject,
                body=text_content or strip_tags(html_content),
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email],
            )
            message.attach_alternative(html_content, 'text/html')
            _send_email_safely(message)

    _email_executor.submit(_send_batch)
    return len(recipients)


def send_competition_launch_notifications(competition):
    """Notifie tous les candidats et abonnés aux alertes qu'un concours vient d'ouvrir."""
    from events.models import CompetitionAlertSubscription
    from .models import User

    candidate_emails = set(
        User.objects.filter(role='candidate', receive_competition_notifications=True)
        .values_list('email', flat=True)
    )
    subscriber_emails = set(CompetitionAlertSubscription.objects.values_list('email', flat=True))
    all_emails = candidate_emails | subscriber_emails

    if not all_emails:
        return 0

    subject = f"Nouveau concours ouvert : {competition.title}"
    text_body = f"""Bonjour,

L'ARSTM vient d'ouvrir un nouveau concours.

{competition.title}
{competition.description}
"""
    if competition.application_deadline:
        text_body += f"\nDate limite de dépôt : {competition.application_deadline.strftime('%d/%m/%Y')}"
    if competition.competition_date:
        text_body += f"\nDate du concours : {competition.competition_date.strftime('%d/%m/%Y')}"
    text_body += "\n\nCordialement,\nL'équipe ARSTM\n"

    html_body = render_to_string('users/emails/competition_launch.html', {
        'subject': subject,
        'competition': competition,
    })

    def _send_batch():
        for email in all_emails:
            message = EmailMultiAlternatives(
                subject=subject,
                body=text_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email],
            )
            message.mixed_subtype = 'related'
            message.attach_alternative(html_body, 'text/html')
            message.attach(_make_logo_attachment())
            _send_email_safely(message)

    _email_executor.submit(_send_batch)
    return len(all_emails)


def send_password_reset_otp_email(user, otp):
    """Envoie le code OTP de réinitialisation de mot de passe à l'utilisateur."""
    subject = "Réinitialisation de votre mot de passe ARSTM"
    text_body = f"""Bonjour {user.get_full_name()},

Voici votre code de vérification pour réinitialiser votre mot de passe :

  {otp}

Ce code est valable 10 minutes. Ne le partagez avec personne.

Si vous n'avez pas demandé cette réinitialisation, ignorez ce message.

Cordialement,
L'équipe ARSTM
"""
    html_body = render_to_string('users/emails/password_reset_otp.html', {
        'subject': subject,
        'full_name': user.get_full_name(),
        'otp': otp,
    })

    recipient = settings.TEST_EMAIL_RECIPIENT or user.email
    email_message = EmailMultiAlternatives(
        subject=subject, body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL, to=[recipient],
    )
    email_message.mixed_subtype = 'related'
    email_message.attach_alternative(html_body, 'text/html')
    email_message.attach(_make_logo_attachment())
    _email_executor.submit(_send_email_safely, email_message)


def send_password_reset_confirmation_email(user, new_password):
    """Confirme la réinitialisation du mot de passe et envoie le nouveau mot de passe à l'utilisateur."""
    subject = "Votre mot de passe ARSTM a été réinitialisé"
    text_body = f"""Bonjour {user.get_full_name()},

Votre mot de passe a été réinitialisé avec succès.

─────────────────────────────
  Identifiant       : {user.email}
  Nouveau mot de passe : {new_password}
─────────────────────────────

Si vous n'êtes pas à l'origine de cette modification, veuillez contacter immédiatement l'équipe ARSTM.

Cordialement,
L'équipe ARSTM
"""
    html_body = render_to_string('users/emails/password_reset_confirmation.html', {
        'subject': subject,
        'full_name': user.get_full_name(),
        'email': user.email,
        'new_password': new_password,
    })

    recipient = settings.TEST_EMAIL_RECIPIENT or user.email
    email_message = EmailMultiAlternatives(
        subject=subject, body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL, to=[recipient],
    )
    email_message.mixed_subtype = 'related'
    email_message.attach_alternative(html_body, 'text/html')
    email_message.attach(_make_logo_attachment())
    _email_executor.submit(_send_email_safely, email_message)


UNSUBSCRIBE_SALT = 'newsletter-unsubscribe'

def generate_unsubscribe_token(email):
    return signing.dumps({'email': email}, salt=UNSUBSCRIBE_SALT)

def verify_unsubscribe_token(token):
    try:
        data = signing.loads(token, salt=UNSUBSCRIBE_SALT)
        return data.get('email')
    except signing.BadSignature:
        return None