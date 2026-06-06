from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    username = serializers.CharField(max_length=150)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def validate_username(self, value):
        if len(value) < 3 or len(value) > 150:
            raise serializers.ValidationError('Имя пользователя должно содержать от 3 до 150 символов.')

        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Пользователь с таким именем уже существует.')

        return value
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            request = self.context.get('request')
            user = authenticate(request, email=email, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError('Пользователь неактивен')
                data['user'] = user
            else:
                raise serializers.ValidationError('Неверные учётные данные')
        else:
            raise serializers.ValidationError('Необходимо указать email и пароль')

        return data















# class SaleSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Sale
#         fields = '__all__'


# class ProductSaleSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Product_sale
#         fields = '__all__'


# class SupplyProductSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Supply_product
#         fields = '__all__'
