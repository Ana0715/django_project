from django.db import models
from django.core.exceptions import ValidationError


def validate_inn(value):
    if not value.isdigit():
        raise ValidationError('ИНН должен содержать только цифры')
    if len(value) not in [10, 12]:
        raise ValidationError('ИНН должен содержать 10 или 12 цифр')


class Company(models.Model):
    inn = models.CharField(verbose_name='ИНН компании', max_length=12, unique=True, null=False, blank=False, validators=[validate_inn])
    company_name = models.CharField(verbose_name='Наименование компании', max_length=255, unique=True, null=False, blank=False)
    owner = models.OneToOneField('authenticate.User', on_delete=models.CASCADE, null=True, blank=True, related_name='owned_companies', verbose_name='Владелец компании')


    class Meta:
        verbose_name = 'Компания'
        verbose_name_plural = 'Компании'
        ordering = ['company_name']

    def __str__(self):
        return f'{self.company_name}, ИНН: {self.inn}'

