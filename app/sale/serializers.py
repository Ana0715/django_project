from rest_framework import serializers
from .models import Sale, ProductSale
from django.db import transaction
from product.models import Product
from django.utils import timezone


class ProductSaleInputSerializer(serializers.Serializer):
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
    

class ProductSaleSerializer(serializers.Serializer):
    product_title = serializers.CharField(source='product.title', read_only=True)
    product_id = serializers.IntegerField(source='product.id', read_only=True)

    class Meta:
        model = ProductSale
        fields = ['product_id', 'product_title', 'quantity']


class SaleSerializer(serializers.Serializer):
    buyer_name = serializers.CharField(max_length=255)
    company = serializers.PrimaryKeyRelatedField(read_only=True)
    sale_date = serializers.DateField(required=False)
    products = ProductSaleInputSerializer(many=True, write_only=True, required=False)
    products_detail = ProductSaleSerializer(many=True, source='sale_products', read_only=True)

    class Meta:
        model = Sale
        fields = ['id', 'buyer_name', 'company', 'sale_date', 'products', 'products_detail']
        read_only_fields = ['company']

    def validate_sale_date(self, value):
        if value and value > timezone.now().date():
            raise serializers.ValidationError('Дата продажи не может быть в будущем.')
        return value

    @transaction.atomic   # операции либо выполнятся целиком, либо откатятся при ошибке
    def create(self, validated_data):
        buyer_name = validated_data.pop('buyer_name')
        products_data = validated_data.pop('products', [])
        if not products_data:
            raise serializers.ValidationError({'products': 'Список товаров не может быть пустым'})
        
        company = self.context['request'].user.company
        if not company:
            raise serializers.ValidationError('Пользователь не принадлежит компании')

        # Предварительная валидация товаров, проверка на дубликаты
        product_ids = [item['id'] for item in products_data]
        if len(product_ids) != len(set(product_ids)):
            raise serializers.ValidationError({'products': 'Обнаружены дубликаты товаров в списке'})

        available_products = list(Product.objects.filter(id__in=product_ids, storage__company=company).select_for_update())  # блокировка строк в БД на время транзакции
        
        found_ids = {p.id for p in available_products}
        missing_ids = set(product_ids) - found_ids

        if missing_ids:
            raise serializers.ValidationError({'products': f'Товары с ID {list(missing_ids)} не найдены или не принадлежат компании'})
        
        sale_products_to_create = []
        products_map = {p.id: p for p in available_products}

        sale = Sale.objects.create(buyer_name=buyer_name, company=company, sale_date=validated_data.get('sale_date', timezone.now().date()))

        for item in products_data:
            product_id = item['id']
            quantity = item['quantity']
            product = products_map[product_id]

            if quantity > product.quantity:
                raise serializers.ValidationError({'products': f'Недостаточно товара с ID {product_id} на складе'})
            
            product.quantity -= quantity
            sale_products_to_create.append(ProductSale(sale=sale, product=product, quantity=quantity))

        
        ProductSale.objects.bulk_create(sale_products_to_create)  #  создаёт все записи в таблице ProductSale одним запросом
        Product.objects.bulk_update(available_products, ['quantity'])  # обновляет поле quantity у всех затронутых товаров одним запросом

        return sale
    


    @transaction.atomic
    def update(self, instance, validated_data):
        # Можно менять только buyer_name и sale_date
        if 'buyer_name' in validated_data:
            instance.buyer_name = validated_data['buyer_name']
        if 'sale_date' in validated_data:
            new_date = validated_data['sale_date']
            if new_date > timezone.now().date():
                raise serializers.ValidationError({'sale_date': 'Дата продажи не может быть в будущем'})
            instance.sale_date = new_date

        instance.save()
        return instance

