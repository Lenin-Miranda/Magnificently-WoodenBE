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
    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request=request, *args, **kwargs)
        data = response.data

        access_token = data.get('access')
        refresh_token = data.get('refresh')

        # Set HttpOnly cookies
        response.set_cookie(
            settings.SIMPLE_JWT["AUTH_COOKIE"],
            value=access_token,
            httponly=True,
            secure=settings.SIMPLE_JWT.get("AUTH_COOKIE_SECURE", False),
            samesite='Lax',
            max_age=60 * 30,
        )

        # Save refresh token too (optional)
        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            httponly=True,
            secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
            max_age=60 * 60 * 24,
        )

        # Don't return tokens in response body
        response.data = {'detail': 'Login successful'}

        return response

class LogoutView(APIView):
    '''
    Logout by deleting the auth cookies
    '''
    def post(self, request):
        response = Response({"message": 'Logout successful'})
        response.delete_cookie("access_token")
        response.delete_cookie('refresh_token')
        return response
    
