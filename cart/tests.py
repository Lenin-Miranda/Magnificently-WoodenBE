from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase
from rest_framework import status

from cart.models import Cart, CartItem
from products.models import Product
from orders.models import Order, OrderItem

User = get_user_model()

class CartCheckoutAPITest(APITestCase):
    '''Tests for the cart checkout process'''
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='cartuser',
            email='cartuser@example.com',
            password='cartpass123',
        )

        # Product with stock
        self.product = Product.objects.create(
            name='Test Product',
            description='A product for testing',
            price=Decimal('50.00'),
            stock=10,
            is_active=True
        )

        # Get the cart that was automatically created by the signal
        self.cart = Cart.objects.get(user=self.user)
        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2,
            price=self.product.price
        )

        self.payload = {
            'shipping_address': '123 Test St, Test City, TC 12345',
            'billing_address': '123 Test St, Test City, TC 12345',
            'payment_method': 'credit_card',
            'shipping_cost': '5.00',
            'tax': '3.00',
        }
    def test_checkout_successful(self):
        '''Test successful checkout'''
        self.client.force_authenticate(user=self.user)
        checkout_url = reverse('cart:cart-checkout')
        response = self.client.post(checkout_url, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.subtotal, Decimal('100.00'))  # 2 items x $50 each
        self.assertEqual(order.shipping_cost, Decimal('5.00'))
        self.assertEqual(order.tax, Decimal('3.00'))
        self.assertEqual(order.total, Decimal('108.00'))  # 100 + 5 + 3
        
        # Verify cart is cleared after checkout
        self.assertEqual(self.cart.items.count(), 0)
        
        # Verify stock is reduced
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 8)  # 10 - 2 = 8
        
        # Verify OrderItem was created
        self.assertEqual(OrderItem.objects.count(), 1)
    
    def test_checkout_insufficient_stock(self):
        '''Test checkout fails due to insufficient stock'''
        self.client.force_authenticate(user=self.user)
        # Update cart item to exceed stock
        self.cart_item.quantity = 20
        self.cart_item.save()
        
        checkout_url = reverse('cart:cart-checkout')
        response = self.client.post(checkout_url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Insufficient stock', response.data['error'])
        self.assertEqual(Order.objects.count(), 0)

    def test_checkout_empty_cart(self):
        '''Test checkout fails with empty cart'''
        self.client.force_authenticate(user=self.user)
        # Clear cart items
        self.cart.items.all().delete()

        checkout_url = reverse('cart:cart-checkout')
        response = self.client.post(checkout_url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Cart is empty', response.data['error'])
        self.assertEqual(Order.objects.count(), 0)

    def test_checkout_unauthenticated(self):
        '''Test checkout fails for unauthenticated user'''
        checkout_url = reverse('cart:cart-checkout')
        response = self.client.post(checkout_url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Order.objects.count(), 0)
    



        


