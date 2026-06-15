# apps/shop/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
import uuid
from .models import Product, Order
from .serializers import ProductSerializer, OrderSerializer
from payments.models import Transaction

class ProductListView(generics.ListAPIView):
    """Liste des études sectorielles, revues et formations courtes"""
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]


class CheckoutView(generics.CreateAPIView):
    """L'utilisateur clique sur 'Acheter' -> Crée la commande et initialise la transaction"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated] # Connexion requise pour acheter et télécharger

    def create(self, request, *args, **kwargs):
        product_id = request.data.get('product')
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response({"error": "Produit introuvable ou inactif."}, status=status.HTTP_404_NOT_FOUND)

        # 1. Création de la commande
        order = Order.objects.create(
            user=request.user,
            product=product,
            total_amount=product.price
        )

        # 2. Génération d'une référence unique pour le paiement Mobile Money
        unique_ref = f"ARSTM-{uuid.uuid4().hex[:10].upper()}"

        # 3. Initialisation de la transaction en attente (Pending)
        transaction = Transaction.objects.create(
            order=order,
            reference=unique_ref,
            amount=order.total_amount,
            status='pending'
        )

        # 4. Réponse au frontend React
        # Ici, dans un vrai projet, on appellerait l'API de l'agrégateur pour récupérer un "payment_url"
        return Response({
            "message": "Commande initialisée",
            "order_id": order.id,
            "transaction_reference": transaction.reference,
            "amount": transaction.amount,
            "payment_url": f"https://mock-gateway.com/pay/{transaction.reference}" # À remplacer par l'URL de votre agrégateur
        }, status=status.HTTP_201_CREATED)