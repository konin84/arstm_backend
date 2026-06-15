from django.db import models
from django.utils.text import slugify

class School(models.Model):
    """
    Composantes de l'ARSTM : ESTM, ESN, CEAM, ISMI.
    Sert de point d'ancrage pour les profils étudiants et les formations.
    """
    name = models.CharField(max_length=255, help_text="Ex: École Supérieure de Navigation (ESN)")
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(verbose_name="Description")
    presentation_video_url = models.URLField(verbose_name="URL Vidéo de présentation", blank=True, null=True)
    featured_image = models.ImageField(upload_to='institution/schools/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Infrastructure(models.Model):
    """
    Équipements et infrastructures pédagogiques de l'Académie (Simulateurs, laboratoires, complexes).
    """
    title = models.CharField(max_length=255, verbose_name="Titre")
    description = models.TextField(verbose_name="Description")
    image = models.ImageField(upload_to='institution/infrastructures/')

    def __str__(self):
        return self.title


class Partner(models.Model):
    """
    Partenariats institutionnels et internationaux (OMI, UEMOA, CEDEAO, Sociétés privées).
    Démontre l'ancrage régional de l'ARSTM.
    """
    PARTNER_TYPE_CHOICES = (
        ('regional', 'Régional / Institutionnel'),
        ('international', 'International'),
        ('corporate', 'Société Privée / Partenaire Métier'),
    )
    name = models.CharField(max_length=255)
    partner_type = models.CharField(max_length=20, choices=PARTNER_TYPE_CHOICES)
    logo = models.ImageField(upload_to='institution/partners/')
    website_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


class Testimonial(models.Model):
    """Témoignages d'anciens élèves et de professionnels formés par l'ARSTM"""
    full_name = models.CharField(max_length=150, verbose_name="Nom complet")
    current_position = models.CharField(max_length=255, verbose_name="Poste actuel / Entreprise")
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True, related_name='testimonials')
    content = models.TextField(verbose_name="Témoignage")
    photo = models.ImageField(upload_to='institution/testimonials/', blank=True, null=True)
    is_featured = models.BooleanField(default=False, verbose_name="Mettre en avant sur la page d'accueil")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return f"{self.full_name} — {self.current_position}"