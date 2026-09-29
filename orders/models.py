from django.conf import settings
from django.db import models

from catalog.models import Product


class Order(models.Model):
    class Status(models.TextChoices):
        PLACED = "placed", "Placed"
        PAID = "paid", "Paid"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    # Allowed status changes. Anything not listed here is rejected.
    TRANSITIONS = {
        Status.PLACED: {Status.PAID, Status.CANCELLED},
        Status.PAID: {Status.SHIPPED, Status.CANCELLED},
        Status.SHIPPED: {Status.DELIVERED},
        Status.DELIVERED: set(),
        Status.CANCELLED: set(),
    }
    # A customer can cancel only before the parcel ships.
    CUSTOMER_CANCELLABLE = {Status.PLACED, Status.PAID}

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="orders", on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLACED)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Shipping details, copied onto the order at checkout time
    ship_name = models.CharField(max_length=100, default="")
    ship_phone = models.CharField(max_length=10, default="")
    ship_address = models.CharField(max_length=255, default="")
    ship_city = models.CharField(max_length=100, default="")
    ship_state = models.CharField(max_length=100, default="")
    ship_pincode = models.CharField(max_length=6, default="")

    class Meta:
        ordering = ["-created_at"]

    def can_move_to(self, new_status):
        return new_status in self.TRANSITIONS[self.status]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)  # price snapshot at purchase time
