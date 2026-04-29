import uuid

from django.contrib.auth import get_user_model
from django.db import models

from products.models import Product

User = get_user_model()


def generate_order_number():
    return uuid.uuid4().hex[:12].upper()


class Order(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PAID = 'paid'
    STATUS_SHIPPED = 'shipped'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_PAID, 'Paid'),
        (STATUS_SHIPPED, 'Shipped'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    ALLOWED_STATUS_TRANSITIONS = {
        STATUS_PENDING: {STATUS_PAID, STATUS_CANCELLED},
        STATUS_PAID: {STATUS_SHIPPED, STATUS_CANCELLED},
        STATUS_SHIPPED: {STATUS_COMPLETED},
        STATUS_COMPLETED: set(),
        STATUS_CANCELLED: set(),
    }

    order_number = models.CharField(
        max_length=20,
        unique=True,
        default=generate_order_number,
        editable=False,
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.TextField(blank=True, default='')
    billing_address = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at', '-id']

    def __str__(self):
        return f"Order {self.order_number}"

    def can_transition_to(self, new_status):
        if self.status == new_status:
            return True
        return new_status in self.ALLOWED_STATUS_TRANSITIONS.get(self.status, set())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='order_items',
    )
    product_name = models.CharField(max_length=200, default='')
    product_slug = models.CharField(max_length=200, blank=True, default='')
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'{self.quantity}x {self.product_name or self.product.name} in Order {self.order.order_number}'

    @property
    def line_total(self):
        return self.price * self.quantity

    def save(self, *args, **kwargs):
        if self.product_id:
            if not self.product_name:
                self.product_name = self.product.name
            if not self.product_slug:
                self.product_slug = self.product.slug or ''
        super().save(*args, **kwargs)

