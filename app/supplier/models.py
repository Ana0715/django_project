from django.db import models
from company.models import Company, validate_inn


class Supplier(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True, related_name='suppliers', verbose_name='Компания поставщика')
    title = models.CharField(verbose_name='Наименование поставщика', max_length=255, unique=True, blank=False, null=False)
    inn = models.CharField(verbose_name='ИНН поставщика', max_length=12, unique=True, blank=False, null=False, validators=[validate_inn])

    class Meta:
        verbose_name = 'Поставщик'
        verbose_name_plural = 'Поставщики'
        ordering = ['title']
        unique_together = ('company', 'title')

    def __str__(self):
        return f'{self.title}, ИНН: {self.inn}'


