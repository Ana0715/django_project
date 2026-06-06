from django.db import models
from storage.models import Storage


class Product(models.Model):
    title = models.CharField(verbose_name='Наименование товара', max_length=255, unique=True, null=False, blank=False)
    purchase_price = models.DecimalField(verbose_name='Закупочная стоимость', max_digits=10, decimal_places=2, null=False, blank=False)
    sale_price = models.DecimalField(verbose_name='Стоимость продажи', max_digits=10, decimal_places=2, null=False, blank=False)
    quantity = models.PositiveIntegerField(verbose_name='Количество на складе', default=0)
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE, related_name='products', blank=False, null=False)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['title']

    def __str__(self):
        return f'{self.title} (Количество: {self.quantity})'
