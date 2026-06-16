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