from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from django.contrib.auth import get_user_model
from .serializes import UserSerializer, RegisterSerializer

User = get_user_model()




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
    


class CookieTokenObtainPairView(TokenObtainPairView):
    '''
    Return access + refresh tokens in HttpOnly cookies
    '''
    permission_classes = [permissions.AllowAny]
    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request=request, *args, **kwargs)
        data = response.data

        access_token = data.get('access')
        refresh_token = data.get('refresh')

        jwt_settings = getattr(settings, 'SIMPLE_JWT', {})
        access_cookie_name = jwt_settings.get('AUTH_COOKIE', 'access_token')
        refresh_cookie_name = jwt_settings.get('REFRESH_COOKIE_NAME', 'refresh_token')
        access_secure = jwt_settings.get('AUTH_COOKIE_SECURE', not settings.DEBUG)
        refresh_secure = jwt_settings.get('AUTH_COOKIE_SECURE', access_secure)
        access_samesite = jwt_settings.get('AUTH_COOKIE_SAMESITE', 'Lax')
        refresh_samesite = jwt_settings.get('AUTH_COOKIE_SAMESITE', access_samesite)

        if access_token:
            response.set_cookie(
                access_cookie_name,
                value=access_token,
                httponly=True,
                secure=access_secure,
                samesite=access_samesite,
                max_age=60 * 30,
            )

        if refresh_token:
            response.set_cookie(
                refresh_cookie_name,
                value=refresh_token,
                httponly=True,
                secure=refresh_secure,
                samesite=refresh_samesite,
                max_age=60 * 60 * 24,
            )

        # Don't return tokens in response body
        response.data = {'detail': 'Login successful'}

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

        response = Response({"message": 'Logout successful'}, status=status.HTTP_200_OK)
        response.delete_cookie(access_cookie_name)
        response.delete_cookie(refresh_cookie_name)
        return response
    
