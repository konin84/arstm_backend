# apps/events/models.py
from django.db import models
from django.utils.text import slugify
from users.models import LookupValue

class Event(models.Model):
    """Agenda dynamique des événements de l'ARSTM (Soutenances, conférences, séminaires)"""
    title = models.CharField(max_length=255, verbose_name="Titre")
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(verbose_name="Description")
    
    start_date = models.DateTimeField(verbose_name="Date et heure de début")
    end_date = models.DateTimeField(verbose_name="Date et heure de fin")
    location = models.CharField(max_length=255, verbose_name="Lieu")
    
    image = models.ImageField(upload_to='events/images/', blank=True, null=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_date']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title) # Se basera automatiquement sur la langue active
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class PromotionBanner(models.Model):
    """Bannières publicitaires et promotionnelles de la page d'accueil"""
    title = models.CharField(max_length=150, verbose_name="Nom de la campagne")
    image = models.ImageField(upload_to='events/banners/', verbose_name="Bannière")
    target_url = models.URLField(verbose_name="Lien de redirection")
    is_active = models.BooleanField(default=True)
    click_count = models.PositiveIntegerField(default=0)
    start_display = models.DateTimeField()
    end_display = models.DateTimeField()

    def __str__(self):
        return self.title


class CompetitionAlertSubscription(models.Model):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=150, blank=True, null=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)


class Competition(models.Model):
    """Concours d'admission ouverts par l'ARSTM."""
    title = models.CharField(max_length=255, verbose_name="Intitulé du concours")
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(verbose_name="Description")
    application_deadline = models.DateField(null=True, blank=True, verbose_name="Date limite de dépôt")
    competition_date = models.DateField(null=True, blank=True, verbose_name="Date du concours")
    is_active = models.BooleanField(default=False, verbose_name="Concours ouvert")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class NewsCategory(LookupValue):
    """Catégorie d'actualité (institutionnelle, communiqué, revue de presse…)."""


class NewsPost(models.Model):
    """Actualités institutionnelles, communiqués de presse et revue de presse de l'ARSTM"""
    title = models.CharField(max_length=255, verbose_name="Titre")
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    category = models.ForeignKey(NewsCategory, on_delete=models.PROTECT, null=True, blank=True, related_name='news_posts')
    content = models.TextField(verbose_name="Contenu")
    featured_image = models.ImageField(upload_to='events/news/', blank=True, null=True)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-published_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title