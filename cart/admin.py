from django.contrib import admin
from .models import Cart, CartItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['subtotal', 'price', 'added_at']
    fields = ['product', 'quantity', 'price', 'subtotal', 'added_at']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'id']
    inlines = [CartItemInline]

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'cart', 'product', 'quantity', 'price', 'added_at', 'subtotal']
    list_filter = ['added_at']
    search_fields = ['cart__user__username', 'product__name', 'id']
    raw_id_fields = ['cart', 'product']
    list_select_related = ['cart', 'product']
    readonly_fields = ['subtotal', 'price', 'added_at']
    ordering = ['-added_at']
    fieldsets = (
        (None, {
            'fields': ('cart', 'product', 'quantity', 'price', 'added_at')
        }),
    )
