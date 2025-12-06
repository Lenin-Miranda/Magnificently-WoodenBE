from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from .models import UserProfile, UserAddress, UserPreferences
    
User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    # Agregar phone_number a los fieldsets
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Información Adicional', {'fields': ('phone_number',)}),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Información Adicional', {'fields': ('phone_number',)}),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'website']
    search_fields = ['user__username', 'location']


@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'street_address', 'city', 'state', 'country', 'is_default']
    list_filter = ['is_default', 'country']
    search_fields = ['user__username', 'city', 'street_address']


@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ['user', 'receive_newsletter', 'preferred_language', 'timezone']
    list_filter = ['receive_newsletter']
    search_fields = ['user__username']
