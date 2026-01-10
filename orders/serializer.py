from rest_framework import serializers
from .models import Order, OrderItem
import uuid

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = [
            'id', 'user', 'order_number', 'status', 'subtotal', 'shipping_cost', 'tax', 'total',
            'shipping_address', 'billing_address', 'created_at', 'updated_at', 'items'
        ]
        read_only_fields = ['id', 'user', 'order_number', 'created_at', 'updated_at']
        extra_kwargs = {
            'shipping_address': {'required': False, 'allow_blank': True},
            'billing_address': {'required': False, 'allow_blank': True}
        }

    def create(self, validated_data):
        # ensure required fields exist when created via API
        if not validated_data.get('order_number'):
            validated_data['order_number'] = uuid.uuid4().hex[:12].upper()
        validated_data.setdefault('shipping_address', '')
        validated_data.setdefault('billing_address', '')
        return super().create(validated_data)
        