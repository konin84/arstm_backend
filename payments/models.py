# payments/models.py
from django.db import models
from django.conf import settings

class Transaction(models.Model):
    PAYMENT_METHODS = (
        ('orange_money', 'Orange Money'),
        ('mtn_momof', 'MTN Mobile Money'),
        ('moov_flooz', 'Moov Money'),
        ('wave', 'Wave'),
        ('card', 'Carte Bancaire'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Initié / En attente'),
        ('success', 'Succès / Payé'),
        ('failed', 'Échoué'),
        ('expired', 'Expiré / Abandonné'),
    )

    # Référence universelle à l'objet qui a déclenché le paiement (Commande, Inscription...)
    # On lie la transaction à une commande générique
    order = models.ForeignKey('shop.Order', on_delete=models.CASCADE, related_name='transactions')
    
    # Identifiants uniques
    reference = models.CharField(max_length=100, unique=True, help_text="ID unique généré par l'ARSTM")
    external_provider_id = models.CharField(max_length=255, blank=True, null=True, help_text="ID retourné par l'agrégateur")
    
    # Détails financiers
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHODS, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Logs techniques pour le débogage en cas de réclamation étudiant
    provider_raw_response = models.JSONField(blank=True, null=True, help_text="Copie brute de la réponse du Webhook")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Tx {self.reference} - {self.amount} FCFA [{self.status}]"