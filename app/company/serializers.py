from rest_framework import serializers
from .models import Company


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'



    # def validate_inn(self, value):
    #     if Company.objects.filter(inn=value).exists():
    #         raise serializers.ValidationError('Компания с таким ИНН уже существует')
    #     return value

    # def validate_company_name(self, value):
    #     if Company.objects.filter(company_name=value).exists():
    #         raise serializers.ValidationError('Компания с таким названием уже существует')
    #     return value
