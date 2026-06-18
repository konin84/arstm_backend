# apps/shop/urls.py
from django.urls import path
from .views import ProductListView, ProductDetailView, CheckoutView

urlpatterns = [
    path('products/', ProductListView.as_view(), name='product_list'),
    path('products/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
]