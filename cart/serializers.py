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
        
        if not product.isActive or product.status != 'available':
            raise serializers.ValidationError({
                'productId': 'This product is not available for purchase'
            })

        # Check stock availability
        if product.inStock < quantity:
            raise serializers.ValidationError({
                'quantity': f'Only {product.inStock} items available in stock'
            })
        
        return data
    
    def create(self, validated_data):
        cart = validated_data['cart']
        product = validated_data['product']
        quantity = validated_data.get('quantity', 1)

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={
                'quantity': quantity,
                'price': product.price,
            },
        )
        if created:
            return item

        new_quantity = item.quantity + quantity
        if product.inStock < new_quantity:
            raise serializers.ValidationError({
                'quantity': f'Only {product.inStock} items available in stock'
            })

        item.quantity = new_quantity
        item.save(update_fields=['quantity'])
        return item
    
    def update(self, instance, validated_data):
        # When updating quantity, check stock again
        if 'quantity' in validated_data:
            quantity = validated_data['quantity']
            if instance.product.inStock < quantity:
                raise serializers.ValidationError({
                    'quantity': f'Only {instance.product.inStock} items available in stock'
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
        if instance.product.inStock < quantity:
            raise serializers.ValidationError({
                'quantity': f'Only {instance.product.inStock} items available in stock'
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
    shipping_address = serializers.CharField(max_length=255, allow_blank=False)
    billing_address = serializers.CharField(max_length=255, required=False, allow_blank=True)
    shipping_cost = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        default=0.00,
        min_value=0,
    )
    tax = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        default=0.00,
        min_value=0,
    )

    def validate(self, attrs):
        if not attrs.get('billing_address'):
            attrs['billing_address'] = attrs['shipping_address']
        return attrs
