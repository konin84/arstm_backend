# apps/shop/urls.py
from django.urls import path
from .views import ProductListView, CheckoutView

urlpatterns = [
    path('products/', ProductListView.as_view(), name='product_list'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
]