from django.urls import path
from .views import (
    CartDetailView,
    CartItemCreateView,
    CartItemUpdateDeleteView,
    CartClearView,
    CreateOrderFromCartView,
)

app_name = 'cart'

urlpatterns = [
    # Get current user's cart
    path('', CartDetailView.as_view(), name='cart-detail'),
    
    # Add item to cart
    path('items/', CartItemCreateView.as_view(), name='cart-item-create'),
    
    # Update (PATCH) or remove (DELETE) cart item
    path('items/<int:id>/', CartItemUpdateDeleteView.as_view(), name='cart-item-detail'),
    
    # Clear all items from cart
    path('clear/', CartClearView.as_view(), name='cart-clear'),
    
    # Create order from cart
    path('checkout/', CreateOrderFromCartView.as_view(), name='cart-checkout'),
]
