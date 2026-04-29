from rest_framework import serializers

from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    line_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'product',
            'product_name',
            'product_slug',
            'quantity',
            'price',
            'line_total',
        ]

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'order_number', 'status', 'subtotal', 'shipping_cost', 'tax', 'total',
            'shipping_address', 'billing_address', 'created_at', 'updated_at', 'items'
        ]
        read_only_fields = fields


class AdminOrderSerializer(OrderSerializer):
    class Meta(OrderSerializer.Meta):
        read_only_fields = [
            'id',
            'user',
            'order_number',
            'subtotal',
            'shipping_cost',
            'tax',
            'total',
            'created_at',
            'updated_at',
            'items',
        ]

    def validate_status(self, value):
        instance = getattr(self, 'instance', None)
        if instance and not instance.can_transition_to(value):
            raise serializers.ValidationError(
                f'Invalid status transition from {instance.status} to {value}.'
            )
        return value
