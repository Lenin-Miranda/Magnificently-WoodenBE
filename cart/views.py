from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer, CartItemUpdateSerializer, CheckoutSerializer
from orders.serializer import OrderSerializer
from orders.services import (
    EmptyCartError,
    InsufficientStockError,
    OrderCreationError,
    UnavailableProductError,
    create_order_from_cart,
)


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
        serializer.save()

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        if request.data.get('quantity') in (0, '0'):
            return Response(status=status.HTTP_204_NO_CONTENT)
        return response


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
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            order = create_order_from_cart(
                user=request.user,
                shipping_address=data['shipping_address'],
                billing_address=data['billing_address'],
                shipping_cost=data['shipping_cost'],
                tax=data['tax'],
            )
        except Cart.DoesNotExist:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        except (EmptyCartError, InsufficientStockError, UnavailableProductError) as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except OrderCreationError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response(
                {'error': 'Failed to create order'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
