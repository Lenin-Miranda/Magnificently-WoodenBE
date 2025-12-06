from django.db import models
from django.contrib.auth.models import AbstractUser

# User model - Extiende AbstractUser para tener toda la funcionalidad de autenticación
class User(AbstractUser):
    # AbstractUser ya tiene: username, email, password, first_name, last_name, 
    # is_active, is_staff, date_joined, last_login
    # Aquí puedes agregar campos adicionales si los necesitas
    phone_number = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return self.username
    
# User Profile model
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"


# User Address model
class UserAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"Address of {self.user.username} - {self.street_address}"

# User Preferences model
class UserPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    receive_newsletter = models.BooleanField(default=True)
    preferred_language = models.CharField(max_length=50, blank=True)
    timezone = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"Preferences of {self.user.username}"

# User Payment Info model
class UserPaymentInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_infos')
    cardholder_name = models.CharField(max_length=100)
    card_number = models.CharField(max_length=16)
    expiration_date = models.DateField()
    billing_address = models.CharField(max_length=255)
    
    def __str__(self):
        return f"Payment Info of {self.user.username} - {self.cardholder_name}"

