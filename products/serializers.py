from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock']
        read_only_fields = ['id']  # generated automatically, never entered by users

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Product name cannot be empty.')
        return value

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError('Price must be greater than zero.')
        return value

    def validate_stock(self, value):
        # IntegerField already rejects non-whole numbers (e.g. 2.5 or "abc")
        if value < 0:
            raise serializers.ValidationError('Stock cannot be negative.')
        return value
