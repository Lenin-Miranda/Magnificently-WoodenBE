from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product
from django.db.models.signals import post_save
from django.dispatch import receiver

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
    # Frozen price: saves product price at the moment of adding to cart
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        # A product can only be 1 time in the cart
        # If you try to add it again, update the quantity
        unique_together = ['cart', 'product']
    
    def __str__(self):
        return f'{self.quantity}x {self.product.name} in cart'
    
    @property
    def subtotal(self):
        # Use frozen price instead of current product price
        return self.price * self.quantity


# Signal: Auto-create cart when user is created
@receiver(post_save, sender=User)
def create_user_cart(sender, instance, created, **kwargs):
    """Automatically create a cart for new users"""
    if created:
        Cart.objects.create(user=instance)