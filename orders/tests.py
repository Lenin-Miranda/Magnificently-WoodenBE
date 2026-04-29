from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal

from orders.models import Order, OrderItem
from products.models import Product
from rest_framework.test import APIClient, APITestCase
from rest_framework import status

User = get_user_model()

class OrderModelTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='orderuser',
            email='orderuser@example.com',
            password='orderpass123',
            first_name='Order',
            last_name='User',
            phone_number='0987654321'
        )
    
    def test_order_creation(self):
        order = Order.objects.create(
            user=self.user,
            subtotal=100.00,
            shipping_cost=10.00,
            tax=5.00,
            total=115.00,
        )
        self.assertEqual(order.user.username, 'orderuser')
        self.assertEqual(order.status, 'pending')
        self.assertEqual(order.total, 115.00)
        self.assertTrue(order.order_number)

class OrderAPITest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='orderapiuser',
            email='orderapiuser@example.com',
            password='orderapipass123',
            first_name='OrderAPI',
            last_name='UserAPI',
            phone_number='1234509876'
        )
        self.order = Order.objects.create(
            user=self.user,
            status='pending',
            subtotal=200.00,
            shipping_cost=15.00,
            tax=10.00,
            total=225.00
        )
        self.order_list_url = reverse('orders:order-list')
        self.order_detail_url = reverse('orders:order-detail', args=[self.order.id])
    def test_order_list_unauthenticated(self):
        response = self.client.get(self.order_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    def test_order_list_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.order_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    def test_order_detail_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.order_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.order.id)
    def test_order_detail_unauthenticated(self):
        response = self.client.get(self.order_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    def test_create_order_authenticated(self):
        self.client.force_authenticate(user=self.user)
        order_data = {
            'status': 'pending',
            'subtotal': 150.00,
            'shipping_cost': 12.00,
            'tax': 8.00,
            'total': 170.00
        }
        response = self.client.post(self.order_list_url, order_data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(Order.objects.count(), 1)
    def test_create_order_unauthenticated(self):
        order_data = {
            'status': 'pending',
            'subtotal': 150.00,
            'shipping_cost': 12.00,
            'tax': 8.00,
            'total': 170.00
        }
        response = self.client.post(self.order_list_url, order_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_order_detail_is_user_scoped(self):
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123',
        )
        other_order = Order.objects.create(
            user=other_user,
            subtotal=50.00,
            shipping_cost=0.00,
            tax=0.00,
            total=50.00,
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('orders:order-detail', args=[other_order.id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class AdminOrderAPITest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username='adminuser',
            email='adminuser@example.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User',
            phone_number='1122334455'
        )
        self.order = Order.objects.create(
            user=self.admin_user,
            status='pending',
            subtotal=300.00,
            shipping_cost=20.00,
            tax=15.00,
            total=335.00
        )
        self.product = Product.objects.create(
            name='Admin Product',
            price=Decimal('300.00'),
            inStock=5,
            isActive=True,
        )
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
            price=Decimal('300.00'),
        )
        self.admin_order_list_url = reverse('orders:admin-order-list')
        self.admin_order_detail_url = reverse('orders:admin-order-detail', args=[self.order.id])
    def test_admin_order_list_authenticated(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.admin_order_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    def test_admin_order_list_unauthenticated(self):
        response = self.client.get(self.admin_order_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    def test_admin_order_detail_authenticated(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.admin_order_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.order.id)
    def test_admin_order_detail_unauthenticated(self):
        response = self.client.get(self.admin_order_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    def test_admin_update_order_authenticated(self):
        self.client.force_authenticate(user=self.admin_user)
        update_data = {
            'status': 'paid'
        }
        response = self.client.patch(self.admin_order_detail_url, update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'paid')
    def test_admin_update_order_unauthenticated(self):
        update_data = {
            'status': 'shipped'
        }
        response = self.client.patch(self.admin_order_detail_url, update_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    def test_admin_update_order_invalid_status(self):
        self.client.force_authenticate(user=self.admin_user)
        update_data = {
            'status': 'invalid_status'
        }
        response = self.client.patch(self.admin_order_detail_url, update_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_update_order_invalid_transition(self):
        self.client.force_authenticate(user=self.admin_user)
        update_data = {
            'status': 'completed'
        }
        response = self.client.patch(self.admin_order_detail_url, update_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid status transition', str(response.data))

    def test_admin_delete_order_is_disabled(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.admin_order_detail_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertTrue(Order.objects.filter(id=self.order.id).exists())

    def test_order_items_keep_product_snapshot(self):
        self.assertEqual(self.order_item.product_name, 'Admin Product')
        self.assertEqual(self.order_item.product_slug, self.product.slug)
