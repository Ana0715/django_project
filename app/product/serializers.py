from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    storage_address = serializers.CharField(source='storage.address', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'title', 'quantity', 'purchase_price', 'sale_price', 'storage', 'storage_address']
        read_only_fields = ['quantity']

    def validate_purchase_price(self, value):
        if value <= 0:
            raise serializers.ValidationError('Закупочная цена должна быть положительной')
        return value

    def validate_sale_price(self, value):
        if value <= 0:
            raise serializers.ValidationError('Цена продажи должна быть положительной')
        return value

