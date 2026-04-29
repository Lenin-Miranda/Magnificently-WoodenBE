from decimal import Decimal

from django.db import transaction

from cart.models import Cart
from products.models import Product

from .models import Order, OrderItem


class OrderCreationError(Exception):
    """Base exception for checkout failures."""


class EmptyCartError(OrderCreationError):
    """Raised when checkout is attempted with no cart items."""


class InsufficientStockError(OrderCreationError):
    """Raised when one or more products do not have enough stock."""


class UnavailableProductError(OrderCreationError):
    """Raised when checkout contains inactive or unavailable products."""


@transaction.atomic
def create_order_from_cart(
    *,
    user,
    shipping_address,
    billing_address,
    shipping_cost,
    tax,
):
    cart = Cart.objects.select_for_update().get(user=user)
    items = list(cart.items.select_related('product').select_for_update())

    if not items:
        raise EmptyCartError('Cart is empty')

    product_ids = [item.product_id for item in items]
    products_by_id = {
        product.id: product
        for product in Product.objects.select_for_update().filter(id__in=product_ids)
    }

    for item in items:
        product = products_by_id[item.product_id]
        if not product.isActive or product.status != 'available':
            raise UnavailableProductError(
                f'{product.name} is not available for checkout.'
            )
        if product.inStock < item.quantity:
            raise InsufficientStockError(
                f'Insufficient stock for {product.name}. Only {product.inStock} available.'
            )

    subtotal = sum(
        (item.price * item.quantity for item in items),
        start=Decimal('0.00'),
    )
    total = subtotal + shipping_cost + tax

    order = Order.objects.create(
        user=user,
        status=Order.STATUS_PENDING,
        subtotal=subtotal,
        shipping_cost=shipping_cost,
        tax=tax,
        total=total,
        shipping_address=shipping_address,
        billing_address=billing_address,
    )

    order_items = []
    for item in items:
        product = products_by_id[item.product_id]
        order_items.append(
            OrderItem(
                order=order,
                product=product,
                product_name=product.name,
                product_slug=product.slug or '',
                quantity=item.quantity,
                price=item.price,
            )
        )
        product.inStock -= item.quantity
        product.save(update_fields=['inStock', 'updated_at'])

    OrderItem.objects.bulk_create(order_items)
    cart.items.filter(id__in=[item.id for item in items]).delete()

    return order
