# apps/payments/serializers.py
from rest_framework import serializers

from events import models
from .models import Transaction

class TransactionSerializer(models.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'order', 'reference', 'external_provider_id', 'amount', 'payment_method', 'status', 'created_at']
        read_only_fields = ['reference', 'status', 'external_provider_id']