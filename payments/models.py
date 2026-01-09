from django.db import models
from django.contrib.auth import get_user_model
from orders.models import Order

User = get_user_model()
# payment model
class Payment(models.Model):
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')

    provider = models.CharField(max_length=50, default='stripe')  # e.g., 'stripe', 'paypal'

    payment_intent_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='usd')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    raw_response = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Payment {self.payment_intent_id} - {self.status}"