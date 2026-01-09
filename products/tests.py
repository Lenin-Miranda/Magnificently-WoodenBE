from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Category, Product, ProductImage
from decimal import Decimal

User = get_user_model()


class CategoryModelTest(TestCase):
    """Tests para el modelo Category"""
    
    def setUp(self):
        self.category = Category.objects.create(
            name='Electronics',
            slug='electronics'
        )
    
    def test_category_creation(self):
        """Verificar que la categoría se crea correctamente"""
        self.assertEqual(self.category.name, 'Electronics')
        self.assertEqual(self.category.slug, 'electronics')
    
    def test_category_str(self):
        """Verificar el método __str__ de Category"""
        self.assertEqual(str(self.category), 'Electronics')


class ProductModelTest(TestCase):
    """Tests para el modelo Product"""
    
    def setUp(self):
        self.category = Category.objects.create(
            name='Electronics',
            slug='electronics'
        )
        self.product = Product.objects.create(
            category=self.category,
            name='Laptop',
            slug='laptop',
            description='A great laptop',
            price=Decimal('999.99'),
            stock=10,
            is_active=True,
            is_featured=False
        )
    
    def test_product_creation(self):
        """Verificar que el producto se crea correctamente"""
        self.assertEqual(self.product.name, 'Laptop')
        self.assertEqual(self.product.price, Decimal('999.99'))
        self.assertEqual(self.product.stock, 10)
        self.assertEqual(self.product.category, self.category)
    
    def test_product_str(self):
        """Verificar el método __str__ de Product"""
        self.assertEqual(str(self.product), 'Laptop')
    
    def test_product_is_active(self):
        """Verificar que el producto está activo por defecto"""
        self.assertTrue(self.product.is_active)


class ProductAPITest(APITestCase):
    """Tests para los endpoints de productos"""
    
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(
            name='Electronics',
            slug='electronics'
        )
        self.product = Product.objects.create(
            category=self.category,
            name='Laptop',
            slug='laptop',
            description='A great laptop',
            price=Decimal('999.99'),
            stock=10,
            is_active=True
        )
        
        # Crear usuario admin para tests de creación/edición
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
    
    def test_get_product_list(self):
        """Test para obtener lista de productos"""
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_product_detail(self):
        """Test para obtener detalle de un producto"""
        url = reverse('product-detail', kwargs={'slug': self.product.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Laptop')
    
    def test_get_categories(self):
        """Test para obtener lista de categorías"""
        url = reverse('category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
