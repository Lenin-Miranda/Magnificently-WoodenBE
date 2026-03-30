from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings


class JWTCookieAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that reads the token from cookies
    instead of the Authorization header
    """
    def authenticate(self, request):
        # Try to get from cookies first
        cookie_name = getattr(settings, 'SIMPLE_JWT', {}).get('AUTH_COOKIE', 'access_token')
        raw_token = request.COOKIES.get(cookie_name)
        
        if raw_token is None:
            # Fall back to header authentication
            return super().authenticate(request)
        
        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token
