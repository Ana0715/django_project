from django.db import models
from django.contrib.auth.models import AbstractUser
from company.models import Company



class User(AbstractUser):
    email = models.EmailField(verbose_name='Email', max_length=255, unique=True, blank=False, null=False)
    is_company_owner = models.BooleanField(verbose_name='Владеет ли компанией', default=False)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, blank=True, null=True,  related_name='employees', verbose_name='Компания')
    is_admin = models.BooleanField(verbose_name='Администратор', default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    def __str__(self):
        return f'{self.username}'
    




# from storage.models import Storage

# class Supplier(models.Model):
#     company = models.OneToOneField(Company, on_delete=models.SET_NULL, blank=True, null=True, related_name='supplier')
#     title = models.CharField(verbose_name='Поставщик', max_length=255, blank=False, null=False)
#     inn = models.CharField(verbose_name='ИНН поставщика', max_length=12, unique=True, blank=False, null=False)

#     class Meta:
#         verbose_name = 'Поставщик'
#         verbose_name_plural = 'Поставщики'
#         ordering = ['title']

#     def __str__(self):
#         return f'{self.title}, ИНН: {self.inn}'


# class Supply(models.Model):
#     supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, blank=False, null=True, related_name='supplies')
#     delivery_date = models.DateTimeField(verbose_name='Дата поставки', auto_now_add=True, blank=False, null=False)

#     class Meta:
#         verbose_name = 'Поставка'
#         verbose_name_plural = 'Поставки'
#         ordering = ['-delivery_date']

#     def __str__(self):
#         return f'Поставщик: {self.supplier}, Дата: {self.delivery_date}'


# class Product(models.Model):
#     title = models.CharField(verbose_name='Наименование товара', max_length=255, unique=True, null=False, blank=False)
#     purchase_price = models.DecimalField(verbose_name='Закупочная стоимость', max_digits=10, decimal_places=2, null=False, blank=False)
#     sale_price = models.DecimalField(verbose_name='Стоимость продажи', max_digits=10, decimal_places=2, null=False, blank=False)
#     quantity = models.PositiveIntegerField(verbose_name='Количество на складе', default=0)
#     storage = models.ForeignKey(Storage, on_delete=models.CASCADE, related_name='products', blank=False, null=False)

#     class Meta:
#         verbose_name = 'Товар'
#         verbose_name_plural = 'Товары'
#         ordering = ['title']

#     def __str__(self):
#         return f'{self.title} (Количество: {self.quantity})'


# class Sale(models.Model):
#     buyer_name = models.CharField(verbose_name='Покупатель', max_length=255, null=False, blank=False)
#     company = models.ForeignKey(Company, on_delete=models.CASCADE, null=False, blank=False, related_name='sales')
#     sale_date = models.DateTimeField(verbose_name='Дата продажи', auto_now_add=True, null=False, blank=False)

#     class Meta:
#         verbose_name = 'Продажа'
#         verbose_name_plural = 'Продажи'
#         ordering = ['-sale_date']

#     def __str__(self):
#         return f'{self.buyer_name}, Дата: {self.sale_date}'


# class Product_sale(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_id_sale', null=False, blank=False)
#     sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='product_sale_id', null=False, blank=False)
#     quantity = models.PositiveIntegerField(verbose_name='Количество в продаже', null=False, blank=False)

#     class Meta:
#         verbose_name = 'Товары текущей продажи'
#         verbose_name_plural = 'Товары текущей продажи'
#         ordering = ['-sale']


# class Supply_product(models.Model):
#     supply = models.ForeignKey(Supply, on_delete=models.CASCADE, related_name='supply_id_product', null=False, blank=False)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='supply_product_id', null=False, blank=False)
#     quantity = models.PositiveIntegerField(verbose_name='Количество в поставке', null=False, blank=False)

#     class Meta:
#         verbose_name = 'Товары текущей поставки'
#         verbose_name_plural = 'Товары текущей поставки'
#         ordering = ['-supply']