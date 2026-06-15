# apps/payments/urls.py
from django.urls import path
from .views import PaymentWebhookView

urlpatterns = [
    # C'est cette URL exacte qu'il faudra renseigner dans le dashboard de votre agrégateur (Orange/MTN/Wave)
    path('webhook/', PaymentWebhookView.as_view(), name='payment_webhook'),
]