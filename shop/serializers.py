# apps/shop/serializers.py
from rest_framework import serializers
from .models import Product, Order

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'slug', 'product_type', 'description', 'price', 'file_attachment', 'is_active']


class OrderSerializer(serializers.ModelSerializer):
    product_detail = ProductSerializer(source='product', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'user_email', 'product', 'product_detail', 'total_amount', 'is_completed', 'created_at']
        read_only_fields = ['total_amount', 'is_completed', 'user']