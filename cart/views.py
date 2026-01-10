from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
import uuid
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer, CartItemUpdateSerializer, CheckoutSerializer
from orders.models import Order, OrderItem


class CartDetailView(generics.RetrieveAPIView):
    """Get current user's cart with all items"""
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Optimize query with prefetch_related
        cart, created = Cart.objects.prefetch_related('items__product').get_or_create(
            user=self.request.user
        )
        return cart


class CartItemCreateView(generics.CreateAPIView):
    """Add item to cart"""
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart=cart)


class CartItemUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """Update cart item quantity (PATCH) or remove item (DELETE)"""
    serializer_class = CartItemUpdateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)
    
    def perform_update(self, serializer):
        # If quantity is 0, the serializer will delete the item
        instance = serializer.save()
        # If item was deleted (quantity was 0), return 204
        if not CartItem.objects.filter(id=instance.id).exists():
            return Response(status=status.HTTP_204_NO_CONTENT)


class CartClearView(APIView):
    """Clear all items from cart"""
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart.items.all().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'message': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)


class CreateOrderFromCartView(APIView):
    '''Create an order from the current user's cart'''
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Validate checkout data using serializer
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        # Extract validated data
        shipping_address = data['shipping_address']
        billing_address = data['billing_address']
        shipping_cost = data['shipping_cost']
        tax = data['tax']
        
        try:
            cart = request.user.cart
        except Cart.DoesNotExist:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Use atomic transaction to ensure data integrity
        try:
            with transaction.atomic():
                # Lock cart items and products to prevent race conditions
                items = cart.items.select_related('product').select_for_update().all()

                if not items.exists():
                    return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
                
                # Validate stock for all items before creating order
                for item in items:
                    if hasattr(item.product, 'stock') and item.product.stock < item.quantity:
                        return Response({
                            'error': f'Insufficient stock for {item.product.name}. Only {item.product.stock} available.'
                        }, status=status.HTTP_400_BAD_REQUEST)
                
                # Calculate totals
                subtotal = cart.total_price
                total = subtotal + shipping_cost + tax
                # Create order with all required fields
                order = Order.objects.create(
                    user=request.user,
                    order_number=uuid.uuid4().hex[:12].upper(),
                    status='pending',
                    subtotal=subtotal,
                    shipping_cost=shipping_cost,
                    tax=tax,
                    total=total,
                    shipping_address=shipping_address,
                    billing_address=billing_address
                )
                
                # Create order items
                for item in items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.price  # Use frozen price from cart
                    )
                    
                    # Optional: Update product stock
                    if hasattr(item.product, 'stock'):
                        item.product.stock -= item.quantity
                        item.product.save()
                
                # Clear the cart after successful order creation
                items.delete()
            
            return Response({
                'order_id': order.id,
                'order_number': order.order_number,
                'total': order.total
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': 'Failed to create order',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
