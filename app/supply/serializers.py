from rest_framework import serializers
from .models import Supply, SupplyProduct
from supplier.serializers import SupplierSerializer
from supplier.models import Supplier
from product.models import Product
from django.db import transaction


class SupplyProductInputSerializer(serializers.Serializer):
    """
    Формат для одного товара в поставке:
    {
        "id": 1,
        "quantity": 8
    }
    """
    id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1)

    def validate(self, data):
        if data['quantity'] <= 0:
            raise serializers.ValidationError({'quantity': 'Количество должно быть положительным'})
        return data


class SupplyProductSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source='product.title', read_only=True)
    product_id = serializers.IntegerField(source='product.id', read_only=True)

    class Meta:
        model = SupplyProduct
        fields = ['product_id', 'product_title', 'quantity']


class SupplySerializer(serializers.ModelSerializer):
    supplier = SupplierSerializer(read_only=True)
    supplier_id = serializers.IntegerField(write_only=True)
    products = SupplyProductInputSerializer(many=True, write_only=True)

    products_detail = SupplyProductSerializer(many=True, source='supply_products', read_only=True)
    delivery_date = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Supply
        fields = ['id', 'supplier', 'supplier_id', 'delivery_date', 'products', 'products_detail',]

    @transaction.atomic
    def create(self, validated_data):
        supplier_id = validated_data.pop('supplier_id')
        products_data = validated_data.pop('products')
        if not products_data:
            raise serializers.ValidationError({'products': 'Список товаров не может быть пустым'})
        
        company = self.context['request'].user.company
        if not company:
            raise serializers.ValidationError('Пользователь не принадлежит компании')

        try:
            supplier = Supplier.objects.get(id=supplier_id, company=company)
        except Supplier.DoesNotExist:
            raise serializers.ValidationError({'supplier_id': 'Поставщик не найден или не принадлежит компании'})

        # Предварительная валидация товаров, проверка на дубликаты
        product_ids = [item['id'] for item in products_data]
        if len(product_ids) != len(set(product_ids)):
            raise serializers.ValidationError({'products': 'Обнаружены дубликаты товаров в списке'})
        
        # available_products = Product.objects.filter(id__in=product_ids, storage__company=company).select_for_update()
        # found_ids = set(available_products.values_list('id', flat=True))
        # missing_ids = set(product_ids) - found_ids

        available_products = list(Product.objects.filter(id__in=product_ids, storage__company=company).select_for_update())
        
        found_ids = {p.id for p in available_products}
        missing_ids = set(product_ids) - found_ids

        if missing_ids:
            raise serializers.ValidationError({'products': f'Товары с ID {list(missing_ids)} не найдены или не принадлежат компании'})

        supply = Supply.objects.create(supplier=supplier, **validated_data)
        
        supply_products_to_create = []

        products_map = {p.id: p for p in available_products}

        for item in products_data:
            product_id = item['id']
            quantity = item['quantity']

            product = products_map[product_id]
            product.quantity += quantity

            supply_products_to_create.append(SupplyProduct(supply=supply, product=product, quantity=quantity))

        
        SupplyProduct.objects.bulk_create(supply_products_to_create)
        Product.objects.bulk_update(available_products, ['quantity'])

        return supply






