# apps/library/models.py
from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    """Catégories dynamiques pour la veille sectorielle (Sûreté maritime, Logistique portuaire, etc.)"""
    name = models.CharField(max_length=100, verbose_name="Nom de la catégorie")
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name = "Catégorie de veille"
        verbose_name_plural = "Catégories de veille"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ResearchPaper(models.Model):
    """Publications scientifiques et espace média du CREMPOL / ISMI"""
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    domain = models.ForeignKey('academic.Domain', on_delete=models.CASCADE)
    authors = models.CharField(max_length=255, help_text="Chercheurs ou Experts ARSTM")
    abstract = models.TextField(help_text="Résumé de la publication")
    pdf_file = models.FileField(upload_to='library/papers/')
    views_count = models.PositiveIntegerField(default=0)
    download_count = models.PositiveIntegerField(default=0)
    created_at = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class SectorWatch(models.Model):
    """Articles d'analyse et de veille sectorielle"""
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    
    # Remplacement du CharField par une relation dynamique ForeignKey
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='articles', verbose_name="Catégorie")
    
    content = models.TextField()
    featured_image = models.ImageField(upload_to='library/watch/')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title