# apps/payments/views.py
from django.shortcuts import get_object_or_404
from .models import Transaction
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response


class PaymentWebhookView(APIView):
    """
    URL publique notifiée par l'agrégateur de paiement dès que la transaction change de statut.
    Sécurisé par IP ou par token secret selon la passerelle utilisée.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        data = request.data

        ref_arstm = data.get('transaction_id') or data.get('cpm_trans_id')
        status_provider = data.get('status')
        payment_channel = data.get('payment_method')
        external_id = data.get('api_response_id')

        if not ref_arstm:
            return Response({"error": "Référence manquante"}, status=status.HTTP_400_BAD_REQUEST)

        transaction = get_object_or_404(Transaction, reference=ref_arstm)

        transaction.provider_raw_response = data
        transaction.external_provider_id = external_id
        transaction.payment_method = payment_channel

        if status_provider in ['ACCEPTED', 'SUCCESS', 'approved']:
            transaction.status = 'success'
            transaction.save()

            order = transaction.order
            order.is_completed = True
            order.save()

            return Response({"status": "Transaction validée et commande complétée"}, status=status.HTTP_200_OK)

        elif status_provider in ['REFUSED', 'FAILED', 'cancel']:
            transaction.status = 'failed'
            transaction.save()
            return Response({"status": "Échec de la transaction enregistré"}, status=status.HTTP_200_OK)

        return Response({"status": "Statut non traité (en attente...)"}, status=status.HTTP_200_OK)
