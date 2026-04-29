from django.contrib import admin
from .models import Order, OrderItem

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'order_number', 'user', 'status', 'total', 'created_at']
    list_filter = ['status', 'created_at']
    list_select_related = ['user']
    search_fields = ['user__username', 'id', 'order_number']
    ordering = ['-created_at', 'user__username', 'status']
    readonly_fields = ['created_at', 'updated_at', 'order_number', 'subtotal', 'shipping_cost', 'tax', 'total']

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

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product_name', 'product', 'quantity', 'price']
    list_filter = ['order__created_at']
    search_fields = ['order__id', 'product__name', 'product_name', 'product_slug']
    ordering = ['order__id', 'product__name']
    raw_id_fields = ['order', 'product']
    list_select_related = ['order', 'product']
    readonly_fields = ['product_name', 'product_slug']

    fieldsets = (
        (None, {
            'fields': ('order', 'product', 'product_name', 'product_slug', 'quantity', 'price')
        }),
    )
