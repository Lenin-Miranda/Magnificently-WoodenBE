from rest_framework import generics, permissions, status
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .serializer import UserSerializer, RegisterSerializer, EmailTokenObtainPairSerializer

User = get_user_model()


def _lifetime_in_seconds(value):
    return int(value.total_seconds())


def _set_auth_cookies(response, access_token=None, refresh_token=None):
    jwt_settings = getattr(settings, 'SIMPLE_JWT', {})
    access_cookie_name = jwt_settings.get('AUTH_COOKIE', 'access_token')
    refresh_cookie_name = jwt_settings.get('REFRESH_COOKIE_NAME', 'refresh_token')
    cookie_secure = jwt_settings.get('AUTH_COOKIE_SECURE', not settings.DEBUG)
    cookie_samesite = jwt_settings.get('AUTH_COOKIE_SAMESITE', 'Lax')
    cookie_path = jwt_settings.get('AUTH_COOKIE_PATH', '/')
    cookie_http_only = jwt_settings.get('AUTH_COOKIE_HTTP_ONLY', True)
    access_cookie_age = _lifetime_in_seconds(jwt_settings['ACCESS_TOKEN_LIFETIME'])
    refresh_cookie_age = _lifetime_in_seconds(jwt_settings['REFRESH_TOKEN_LIFETIME'])

    if access_token:
        response.set_cookie(
            access_cookie_name,
            value=access_token,
            httponly=cookie_http_only,
            secure=cookie_secure,
            samesite=cookie_samesite,
            path=cookie_path,
            max_age=access_cookie_age,
        )

    if refresh_token:
        response.set_cookie(
            refresh_cookie_name,
            value=refresh_token,
            httponly=cookie_http_only,
            secure=cookie_secure,
            samesite=cookie_samesite,
            path=cookie_path,
            max_age=refresh_cookie_age,
        )




@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(generics.CreateAPIView):
    '''
    Register a new user
    '''
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class MeView(APIView):
    '''
    Get current logged in user info
    '''
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    


@method_decorator(csrf_exempt, name='dispatch')
class CookieTokenObtainPairView(TokenObtainPairView):
    '''
    Return access + refresh tokens in HttpOnly cookies
    '''
    permission_classes = [permissions.AllowAny]
    serializer_class = EmailTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request=request, *args, **kwargs)
        data = response.data

        access_token = data.get('access')
        refresh_token = data.get('refresh')

        _set_auth_cookies(response, access_token=access_token, refresh_token=refresh_token)

        # Don't return tokens in response body
        response.data = {'detail': 'Login successful'}

        return response


@method_decorator(csrf_exempt, name='dispatch')
class CookieTokenRefreshView(TokenRefreshView):
    '''
    Refresh access + rotated refresh tokens using the HttpOnly refresh cookie
    '''
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        jwt_settings = getattr(settings, 'SIMPLE_JWT', {})
        refresh_cookie_name = jwt_settings.get('REFRESH_COOKIE_NAME', 'refresh_token')
        refresh_token = request.COOKIES.get(refresh_cookie_name) or request.data.get('refresh')

        serializer = self.get_serializer(data={'refresh': refresh_token})
        serializer.is_valid(raise_exception=True)

        access_token = serializer.validated_data.get('access')
        rotated_refresh_token = serializer.validated_data.get('refresh')

        response = Response({'detail': 'Token refreshed successfully'}, status=status.HTTP_200_OK)
        _set_auth_cookies(
            response,
            access_token=access_token,
            refresh_token=rotated_refresh_token,
        )
        return response

class LogoutView(APIView):
    '''
    Logout by deleting the auth cookies
    '''
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        jwt_settings = getattr(settings, 'SIMPLE_JWT', {})
        access_cookie_name = jwt_settings.get('AUTH_COOKIE', 'access_token')
        refresh_cookie_name = jwt_settings.get('REFRESH_COOKIE_NAME', 'refresh_token')
        cookie_path = jwt_settings.get('AUTH_COOKIE_PATH', '/')

        response = Response({"message": 'Logout successful'}, status=status.HTTP_200_OK)
        response.delete_cookie(access_cookie_name, path=cookie_path)
        response.delete_cookie(refresh_cookie_name, path=cookie_path)
        return response
    
