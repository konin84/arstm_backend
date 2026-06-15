# shop/models.py
from django.db import models
from django.conf import settings
from django.utils.text import slugify

class Product(models.Model):
    PRODUCT_TYPE = (
        ('publication', 'Publication Scientifique / Revue'),
        ('study', 'Étude Sectorielle'),
        ('formation_continue', 'Module Court / FOAD'),
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    product_type = models.CharField(max_length=30, choices=PRODUCT_TYPE)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Prix en FCFA")
    file_attachment = models.FileField(upload_to='shop/products/', blank=True, null=True, help_text="Fichier si produit numérique")
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey('shop.Product', on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Statut métier de la commande
    is_completed = models.BooleanField(default=False, help_text="Devient True dès qu'une transaction associée passe à 'success'")
    created_at = models.DateTimeField(auto_now_add=True)