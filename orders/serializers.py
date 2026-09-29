import re

from rest_framework import serializers

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["product", "product_name", "quantity", "unit_price"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "status", "total", "created_at", "updated_at",
            "ship_name", "ship_phone", "ship_address", "ship_city", "ship_state", "ship_pincode",
            "items",
        ]


class CheckoutSerializer(serializers.Serializer):
    """Shipping details the customer must give at checkout (Indian format)."""
    ship_name = serializers.CharField(max_length=100)
    ship_phone = serializers.CharField(max_length=10)
    ship_address = serializers.CharField(max_length=255)
    ship_city = serializers.CharField(max_length=100)
    ship_state = serializers.CharField(max_length=100)
    ship_pincode = serializers.CharField(max_length=6)

    def validate_ship_phone(self, value):
        if not re.fullmatch(r"[6-9]\d{9}", value):
            raise serializers.ValidationError("Enter a valid 10-digit Indian mobile number.")
        return value

    def validate_ship_pincode(self, value):
        if not re.fullmatch(r"[1-9]\d{5}", value):
            raise serializers.ValidationError("Enter a valid 6-digit pincode.")
        return value


class StatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.Status.choices)
