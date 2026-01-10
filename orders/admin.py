from django.contrib import admin
from .models import Order, OrderItem

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total','order_number', 'created_at']
    list_filter = ['status', 'created_at']
    list_select_related = ['user']
    search_fields = ['user__username', 'id', 'order_number']
    ordering = ['-created_at', 'user__username', 'status']
    readonly_fields = ['created_at', 'updated_at', 'order_number']

    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'shipping_cost', 'tax', 'total')
        }),
        ('Addresses', {
            'fields': ('shipping_address', 'billing_address')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'quantity', 'price']
    list_filter = ['order__created_at']
    search_fields = ['order__id', 'product__name']
    ordering = ['order__id', 'product__name']
    raw_id_fields = ['order', 'product']
    list_select_related = ['order', 'product']

    fieldsets = (
        (None, {
            'fields': ('order', 'product', 'quantity', 'price')
        }),
    )