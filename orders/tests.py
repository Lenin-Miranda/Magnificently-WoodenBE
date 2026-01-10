from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from orders.models import Order
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
        # create instance without saving to avoid NOT NULL constraint on DB
        order = Order()
        order.user = self.user
        order.order_number = 'TEST12345'
        order.status = 'pending'
        order.subtotal = 100.00
        order.shipping_cost = 10.00
        order.tax = 5.00
        order.total = 115.00
        order.shipping_address = 'N/A'
        order.billing_address = 'N/A'
        order.save()
        self.assertEqual(order.user.username, 'orderuser')
        self.assertEqual(order.status, 'pending')
        self.assertEqual(order.total, 115.00)

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
        self.assertEqual(len(response.data), 1)
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
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 2)
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
            'status': 'shipped'
        }
        response = self.client.patch(self.admin_order_detail_url, update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'shipped')
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
    def test_admin_delete_order(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.admin_order_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(id=self.order.id).exists())
    