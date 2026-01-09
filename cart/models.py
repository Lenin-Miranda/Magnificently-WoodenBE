from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product

User = get_user_model()

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart' )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Cart of {self.user.username}'
    
    @property
    def total_items(self):
        '''Calculate the total of itesm in the cart'''
        return sum(item.quantity for item in self.items.all())
    
    @property
    def total_price(self):
        """Calculate the total price of the cart"""
        return sum(item.subtotal for item in self.items.all())
    

class CartItem(models.Model):
    """Individual items in the cart"""
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items' # To access cart.items.all()
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )

    quantity = models.PositiveBigIntegerField(default=1) # Quantity of the product
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # A product can only be 1 time in the cart
        # If you try to add it again, update the quantity
        unique_together = ['cart', 'product']
    
    def __str__(self):
        return f'{self.quantity}x {self.product.name} in cart'
    
    @property
    def subtotal(self):
        return self.product.price * self.quantity
    