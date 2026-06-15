from django.db import models
from django.utils.text import slugify

class Domain(models.Model):
    """Domaines d'expertise / Filières (Maritime, Portuaire, Logistique, Industriel)"""
    name = models.CharField(max_length=100, verbose_name="Nom")
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Program(models.Model):
    """Formations offertes (Initiale ou Continue) par les composantes de l'ARSTM"""
    PROGRAM_TYPE_CHOICES = (
        ('initiale', 'Formation Initiale'), 
        ('continue', 'Formation Continue')
    )
    REGIME_CHOICES = (
        ('sedentaire', 'Sédentaire'),
        ('navigant', 'Navigant'),
    )
    
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, related_name='programs')
    school = models.ForeignKey('institution.School', on_delete=models.CASCADE, related_name='programs')
    
    title = models.CharField(max_length=255, verbose_name="Titre")
    slug = models.SlugField(unique=True, blank=True)

    program_type = models.CharField(max_length=20, choices=PROGRAM_TYPE_CHOICES)
    regime = models.CharField(max_length=20, choices=REGIME_CHOICES, default='sedentaire')
    duration = models.CharField(max_length=100, help_text="Ex: 3 ans, 12 mois")

    description = models.TextField(verbose_name="Description")
    career_opportunities = models.TextField(verbose_name="Débouchés professionnels", help_text="Séparés par des retours à la ligne")
    
    is_active = models.BooleanField(default=True)

    # --- Éléments cruciaux pour le SEO ---
    meta_title = models.CharField(max_length=70, blank=True, help_text="Titre SEO pour Google (max 70 car.)")
    meta_description = models.CharField(max_length=160, blank=True, help_text="Description SEO pour Google (max 160 car.)")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Document(models.Model):
    """Plaquettes de formation, brochures PDF téléchargeables"""
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='documents', blank=True, null=True)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='academic/brochures/')
    download_count = models.PositiveIntegerField(default=0, verbose_name="Nombre de téléchargements (KPI)")

    def __str__(self):
        return self.title