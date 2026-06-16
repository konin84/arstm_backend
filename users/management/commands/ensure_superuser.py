import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    """
    Crée un superutilisateur à partir de variables d'environnement, si aucun
    utilisateur n'existe encore avec cet email. Idempotent — sans danger à
    exécuter à chaque déploiement (utile sur Render free tier, sans accès Shell).

    Variables requises : DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_PASSWORD,
    DJANGO_SUPERUSER_FIRST_NAME, DJANGO_SUPERUSER_LAST_NAME.
    Si l'une d'elles est absente, la commande ne fait rien (silencieux).
    """

    help = "Crée un superutilisateur depuis les variables d'environnement DJANGO_SUPERUSER_* s'il n'existe pas déjà."

    def handle(self, *args, **options):
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
        first_name = os.environ.get('DJANGO_SUPERUSER_FIRST_NAME')
        last_name = os.environ.get('DJANGO_SUPERUSER_LAST_NAME')

        if not all([email, password, first_name, last_name]):
            self.stdout.write("DJANGO_SUPERUSER_* non défini(s) — étape ignorée.")
            return

        if User.objects.filter(email=email).exists():
            self.stdout.write(f"Superutilisateur '{email}' déjà existant — rien à faire.")
            return

        User.objects.create_superuser(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        self.stdout.write(self.style.SUCCESS(f"Superutilisateur '{email}' créé."))
