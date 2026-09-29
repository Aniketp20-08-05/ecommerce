"""Business logic for checkout, cancellation and status changes.

Inventory consistency: everything runs inside one DB transaction, and the
product rows are locked with SELECT ... FOR UPDATE (ordered by id to avoid
deadlocks). Two customers buying the last unit at the same time are
serialized: the second one sees stock = 0 and gets a clean error.
"""
import logging
from decimal import Decimal

from django.db import transaction

from cart.models import Cart
from catalog.models import Product

from .models import Order, OrderItem

logger = logging.getLogger(__name__)


class CheckoutError(Exception):
    pass


@transaction.atomic
def place_order(user, shipping):
    """Turn the user's cart into an order. `shipping` is a dict of validated address fields."""
    try:
        cart = Cart.objects.get(user=user)
    except Cart.DoesNotExist:
        raise CheckoutError("Your cart is empty.")

    items = list(cart.items.select_related("product").order_by("product_id"))
    if not items:
        raise CheckoutError("Your cart is empty.")

    # Lock the product rows so concurrent checkouts can't oversell.
    products = {
        p.id: p
        for p in Product.objects.select_for_update().filter(id__in=[i.product_id for i in items]).order_by("id")
    }

    total = Decimal("0.00")
    for item in items:
        product = products[item.product_id]
        if not product.is_active:
            raise CheckoutError(f"'{product.name}' is no longer available.")
        if product.stock < item.quantity:
            raise CheckoutError(f"Only {product.stock} unit(s) of '{product.name}' left in stock.")
        total += product.price * item.quantity

    order = Order.objects.create(user=user, total=total, **shipping)
    for item in items:
        product = products[item.product_id]
        product.stock -= item.quantity
        product.save(update_fields=["stock"])
        OrderItem.objects.create(order=order, product=product, quantity=item.quantity, unit_price=product.price)

    cart.items.all().delete()
    logger.info("order placed id=%s user=%s total=%s", order.id, user.id, order.total)
    return order


def _restock(order):
    for item in order.items.select_related("product").order_by("product_id"):
        product = Product.objects.select_for_update().get(pk=item.product_id)
        product.stock += item.quantity
        product.save(update_fields=["stock"])


@transaction.atomic
def cancel_order(order):
    """Customer cancellation: allowed only before shipping. Stock goes back on the shelf."""
    order = Order.objects.select_for_update().get(pk=order.pk)
    if order.status == Order.Status.CANCELLED:
        raise CheckoutError("Order is already cancelled.")
    if order.status not in Order.CUSTOMER_CANCELLABLE:
        raise CheckoutError(f"An order that is '{order.status}' can no longer be cancelled.")
    _restock(order)
    order.status = Order.Status.CANCELLED
    order.save(update_fields=["status", "updated_at"])
    logger.info("order cancelled id=%s", order.id)
    return order


@transaction.atomic
def change_status(order, new_status):
    """Staff-driven status change, validated against Order.TRANSITIONS."""
    order = Order.objects.select_for_update().get(pk=order.pk)
    if new_status not in Order.Status.values:
        raise CheckoutError(f"Unknown status '{new_status}'.")
    if not order.can_move_to(new_status):
        raise CheckoutError(f"Cannot move an order from '{order.status}' to '{new_status}'.")
    if new_status == Order.Status.CANCELLED:
        _restock(order)
    order.status = new_status
    order.save(update_fields=["status", "updated_at"])
    logger.info("order id=%s status -> %s", order.id, new_status)
    return order
