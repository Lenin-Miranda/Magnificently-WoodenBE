from rest_framework import serializers
from .models import Cart, CartItem
from products.models import Product
from products.serializer import ProductSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    productId = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'productId', 'quantity', 'price', 'subtotal', 'added_at']
        read_only_fields = ['id', 'price', 'subtotal', 'added_at']

    def validate(self, data):
        product = data.get('product')
        quantity = data.get('quantity', 1)
        
        # Validate quantity is positive
        if quantity <= 0:
            raise serializers.ValidationError({
                'quantity': 'Quantity must be greater than zero'
            })
        
        # Check stock availability
        if hasattr(product, 'stock') and product.stock < quantity:
            raise serializers.ValidationError({
                'quantity': f'Only {product.stock} items available in stock'
            })
        
        return data
    
    def create(self, validated_data):
        # Freeze price when adding to cart
        validated_data['price'] = validated_data['product'].price
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # When updating quantity, check stock again
        if 'quantity' in validated_data:
            quantity = validated_data['quantity']
            if hasattr(instance.product, 'stock') and instance.product.stock < quantity:
                raise serializers.ValidationError({
                    'quantity': f'Only {instance.product.stock} items available in stock'
                })
        return super().update(instance, validated_data)


class CartItemUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating cart item quantity only"""
    
    class Meta:
        model = CartItem
        fields = ['quantity']
    
    def validate_quantity(self, value):
        # Allow 0 or negative to trigger deletion
        if value < 0:
            raise serializers.ValidationError('Quantity cannot be negative')
        return value
    
    def update(self, instance, validated_data):
        quantity = validated_data.get('quantity')
        
        # If quantity is 0, delete the item
        if quantity == 0:
            instance.delete()
            return instance
        
        # Check stock availability
        if hasattr(instance.product, 'stock') and instance.product.stock < quantity:
            raise serializers.ValidationError({
                'quantity': f'Only {instance.product.stock} items available in stock'
            })
        
        instance.quantity = quantity
        instance.save()
        return instance


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_items', 'total_price', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'total_items', 'total_price']


class CheckoutSerializer(serializers.Serializer):
    shipping_address = serializers.CharField(max_length=255, required=False, allow_blank=True)
    billing_address = serializers.CharField(max_length=255, required=False, allow_blank=True)
    shipping_cost = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0.00)
    tax = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0.00)
    