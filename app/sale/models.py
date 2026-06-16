from django.db import models
from company.models import Company
from product.models import Product
from django.core.exceptions import ValidationError
from django.utils import timezone


class Sale(models.Model):
    buyer_name = models.CharField(verbose_name='Покупатель', blank=False, null=False, max_length=255)
    company = models.ForeignKey(Company, verbose_name='Компания', on_delete=models.CASCADE, blank=False, null=False, related_name='sales')
    sale_date = models.DateField(verbose_name='Дата продажи')

    class Meta:
        verbose_name = 'Продажа'
        verbose_name_plural = 'Продажи'
        ordering = ['-sale_date']

    def clean(self):
        # sale_date не в будущем
        if self.sale_date and self.sale_date > timezone.now().date():
            raise ValidationError('Дата продажи не может быть в будущем.')

    def __str__(self):
        return f'Продажа №{self.id}, дата: {self.sale_date}'


class ProductSale(models.Model):
    sale = models.ForeignKey(Sale,verbose_name='Продажа', on_delete=models.CASCADE, blank=False, null=False, related_name='sale_products')
    product = models.ForeignKey(Product, verbose_name='Товар', on_delete=models.CASCADE, blank=False, null=False,related_name='product_sales')
    quantity = models.PositiveIntegerField(verbose_name='Количество товара в продаже')

    class Meta:
        verbose_name = 'Товар в продаже'
        verbose_name_plural = 'Товары в продажах'
        unique_together = ('sale', 'product')

    def clean(self):
        if self.pk and self.sale.company != self.product.storage.company:
            raise ValidationError('Продажа и товар должны принадлежать одной компании')
        if self.quantity <= 0:
            raise ValidationError({'quantity': 'Количество должно быть положительным.'})

    def __str__(self):
        return f'{self.product.title} - {self.quantity} шт. в продаже {self.sale.id}'
    