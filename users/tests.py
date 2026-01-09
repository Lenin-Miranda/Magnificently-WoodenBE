from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class UserModelTest(TestCase):
    """Tests para el modelo User"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            phone_number='1234567890'
        )
    
    def test_user_creation(self):
        """Verificar que el usuario se crea correctamente"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('testpass123'))
    
    def test_user_str(self):
        """Verificar el método __str__ del usuario"""
        self.assertEqual(str(self.user), 'testuser')


class UserAuthenticationAPITest(APITestCase):
    """Tests para los endpoints de autenticación"""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('users:register')
        self.login_url = reverse('users:login')
        self.me_url = reverse('users:me')
        
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '1234567890'
        }
    
    def test_user_registration(self):
        """Test de registro de usuario"""
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='testuser').exists())
    
    def test_user_login(self):
        """Test de login de usuario"""
        # Crear usuario primero
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Intentar login
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_user_profile(self):
        """Test para obtener perfil de usuario autenticado"""
        # Crear y autenticar usuario
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=user)
        
        # Obtener perfil
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
    
    def test_get_user_profile_unauthenticated(self):
        """Test que usuario no autenticado no puede acceder a /me/"""
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
