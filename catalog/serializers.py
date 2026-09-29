from rest_framework import serializers

from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class ProductSerializer(serializers.ModelSerializer):
    retailer = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Product
        fields = ["id", "category", "retailer", "name", "description", "price", "stock", "is_active"]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value
