from django.db import models
from django.utils.text import slugify
from users.models import LookupValue

class Domain(models.Model):
    """Domaines d'expertise / Filières (Maritime, Portuaire, Logistique, Industriel)"""
    name = models.CharField(max_length=255, verbose_name="Nom")
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if self.pk:
            original = Domain.objects.filter(pk=self.pk).values_list('name', flat=True).first()
            if original != self.name:
                self.slug = slugify(self.name)
        elif not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
                                                    
    def __str__(self):
        return self.name


class ProgramType(LookupValue):
    """Type de formation (professionnelle, continue…)."""


class Regime(LookupValue):
    """Régime de formation (sédentaire, navigant…)."""


class Program(models.Model):
    """Formations offertes (professionnelle ou Continue) par les composantes de l'ARSTM"""
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, related_name='programs')
    school = models.ForeignKey('institution.School', on_delete=models.CASCADE, related_name='programs')

    title = models.CharField(max_length=255, verbose_name="Titre")
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    program_type = models.ForeignKey(ProgramType, on_delete=models.PROTECT, related_name='programs')
    regime = models.ForeignKey(Regime, on_delete=models.PROTECT, related_name='programs', null=True, blank=True)
    duration = models.CharField(max_length=100, help_text="Ex: 3 ans, 12 mois")

    description = models.TextField(verbose_name="Description")
    career_opportunities = models.TextField(verbose_name="Débouchés professionnels", help_text="Séparés par des retours à la ligne")
    
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.pk:
            original = Program.objects.filter(pk=self.pk).values_list('title', flat=True).first()
            if original != self.title:
                self.slug = slugify(self.title)
        elif not self.slug:
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