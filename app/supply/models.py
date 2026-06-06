from django.db import models
from supplier.models import Supplier
from product.models import Product
from django.core.exceptions import ValidationError

    
class Supply(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, blank=False, null=False, related_name='supplies', verbose_name='Поставщик')
    delivery_date = models.DateTimeField(verbose_name='Дата поставки', auto_now_add=True)

    class Meta:
        verbose_name = 'Поставка'
        verbose_name_plural = 'Поставки'
        ordering = ['-delivery_date']

    def __str__(self):
        return f'Поставка №{self.id}, поставщик: {self.supplier.title}'


class SupplyProduct(models.Model):
    supply = models.ForeignKey(Supply, on_delete=models.CASCADE, blank=False, null=False, verbose_name='Поставка', related_name='supply_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=False, null=False, verbose_name='Товар', related_name='product_supplies')
    quantity = models.PositiveIntegerField(verbose_name='Количество товара в поставке')

    class Meta:
        verbose_name = 'Товар в поставке'
        verbose_name_plural = 'Товары в поставках'
        unique_together = ('supply', 'product')
        # индекс для ускорения фильтрации?
        indexes = [
            models.Index(fields=['supply', 'product']),
        ]

    def clean(self):
        if self.pk and self.supply.supplier.company != self.product.storage.company:
            raise ValidationError('Поставщик и товар должны принадлежать одной компании')
        

    def delete(self, *args, **kwargs):
        raise PermissionError('Удаление записей о товарах в поставках запрещено')


    def __str__(self):
        return f'{self.product.title} - {self.quantity} шт. в поставке {self.supply.id}'
