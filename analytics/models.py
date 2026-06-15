# apps/analytics/models.py
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class ContentTraffic(models.Model):
    """Suivi centralisé et anonyme des interactions pour les rapports de performance de la DCM"""
    ACTION_CHOICES = (
        ('click', 'Clic'),
        ('download', 'Téléchargement'),
        ('view', 'Vue'),
    )

    # Configuration de la relation générique Django
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    visitor_country = models.CharField(max_length=50, blank=True, null=True, default="CI", help_text="Code pays ISO (ex: CI, BF, SN)")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.get_action_display()} sur {self.content_type.model} ({self.object_id}) - {self.visitor_country}"