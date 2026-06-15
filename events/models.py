# apps/events/models.py
from django.db import models
from django.utils.text import slugify

class Event(models.Model):
    """Agenda dynamique des événements de l'ARSTM (Soutenances, conférences, séminaires)"""
    title = models.CharField(max_length=255, verbose_name="Titre")
    slug = models.SlugField(unique=True, blank=True)
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


class NewsPost(models.Model):
    """Actualités institutionnelles, communiqués de presse et revue de presse de l'ARSTM"""
    CATEGORY_CHOICES = (
        ('actualite', 'Actualité institutionnelle'),
        ('communique', 'Communiqué de presse'),
        ('revue_presse', 'Revue de presse'),
    )

    title = models.CharField(max_length=255, verbose_name="Titre")
    slug = models.SlugField(unique=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='actualite')
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