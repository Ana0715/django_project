from django.db import models
from company.models import Company
    

class Storage(models.Model):
    address = models.CharField(verbose_name='Адрес склада', max_length=255, blank=False, null=False)
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='storage', verbose_name='Компания склада')

    class Meta:
        verbose_name = 'Склад'
        verbose_name_plural = 'Склады'
        ordering = ['address']

    def __str__(self):
        return f'{self.company}, Адрес: {self.address}'

