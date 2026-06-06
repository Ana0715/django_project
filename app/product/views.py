from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiRequest, OpenApiResponse
from .serializers import ProductSerializer
from .models import Product
from storage.models import Storage
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied


@extend_schema(
    description='Эндпоинт создания товара',
    tags=['Product'],
    request=OpenApiRequest(
        request={
            'type': 'object',
            'properties': {
                'title': {
                    'type': 'string',
                    'example': 'Игровая клавиатура'
                },
                'purchase_price': {
                    'type': 'string',
                    'example': '1199.99'
                },
                'sale_price': {
                    'type': 'string',
                    'example': '2499.99'
                },
            }
        }
    ),
    responses={
        201: OpenApiResponse(response=ProductSerializer, description='Товар успешно создан'),
        400: OpenApiResponse(description='Неверные данные или ошибка валидации'),
        403: OpenApiResponse(description='Нет прав на создание товара'),
    }
)
class CreateProductView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        company = request.user.company
        if not company:
            return Response({'error': 'Пользователь не является сотрудником компании'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            storage = company.storage
        except:
            return Response({'error': 'У компании нет склада'}, status=status.HTTP_400_BAD_REQUEST)
        
        title = request.data.get('title')        

        if Product.objects.filter(title=title, storage=storage).exists():
            return Response({'error': 'Такой товар уже существует на данном складе'}, status=status.HTTP_400_BAD_REQUEST)

        data=request.data
        data['storage'] = storage.id

        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    description='Эндпоинт получения товара',
    tags=['Product'],
    responses={
        200: OpenApiResponse(response=ProductSerializer, description='Данные товара'),
        400: OpenApiResponse(description='Неверные данные или ошибка валидации'),
        403: OpenApiResponse(description='Нет прав на получение данных товара'),
        404: OpenApiResponse(description='Товар не найден'),
    }
)
class GetProductView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, product_id):
        company = request.user.company

        if not company:
            return Response({'error': 'Пользователь не принадлежит компании'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            storage = company.storage
            product = Product.objects.get(id=product_id, storage=storage)
            serializer = ProductSerializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Storage.DoesNotExist:
            return Response({'error': 'У компании нет склада'}, status=status.HTTP_404_NOT_FOUND)
        except Product.DoesNotExist:
            return Response({'error': 'Товар не найден'}, status=status.HTTP_404_NOT_FOUND)
        

@extend_schema(
    description='Эндпоинт получения списка товаров компании',
    tags=['Product'],
    responses={
        200: OpenApiResponse(response=ProductSerializer(many=True), description='Список товаров'),
        400: OpenApiResponse(description='Неверные данные или ошибка валидации'),
        403: OpenApiResponse(description='Нет доступа к товарам'),
        404: OpenApiResponse(description='Товар не найден'),
    }
)
class GetProductsListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        company = request.user.company

        if not company:
            raise PermissionDenied("Пользователь не принадлежит компании")

        try:
            storage = company.storage
        except Storage.DoesNotExist:
            return Response({'error': 'У компании нет склада'}, status=status.HTTP_400_BAD_REQUEST)

        products = Product.objects.filter(storage=storage)
        if not products:
            return Response({'error': 'Товары не найдены'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

@extend_schema(
    description='Эндпоинт редактирования товара',
    tags=['Product'],
    request=OpenApiRequest(
        request={
            'type': 'object',
            'properties': {
                'title': {
                    'type': 'string',
                    'example': 'Игровая клавиатура',
                    'required': False
                },
                'purchase_price': {
                    'type': 'string',
                    'example': '1199.99',
                    'required': False
                },
                'sale_price': {
                    'type': 'string',
                    'example': '2499.99',
                    'required': False
                },
            }
        }
    ),
    responses={
        200: OpenApiResponse(response=ProductSerializer, description='Товар успешно обновлён'),
        400: OpenApiResponse(description='Неверные данные или ошибка валидации'),
        404: OpenApiResponse(description='Товар не найден'),
        403: OpenApiResponse(description='Нет прав на редактирование товара'),
    }
)
class UpdateProductView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, product_id):
        company = request.user.company

        if not company:
            return Response({'error': 'Пользователь не принадлежит компании'}, status=status.HTTP_403_FORBIDDEN)

        try:
            product = Product.objects.get(id=product_id)
            storage = Storage.objects.get(id=company.storage.id)
        except Product.DoesNotExist:
            return Response({'error': 'Товар не найден'}, status=status.HTTP_404_NOT_FOUND)
        except Storage.DoesNotExist:
            return Response({'error': 'Склад компании не найден'}, status=status.HTTP_404_NOT_FOUND)

        if product.storage.company != company:
            raise PermissionDenied("Нет доступа к товару")

        data=request.data
        data['storage'] = storage.id
        
        serializer = ProductSerializer(product, data=data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    description='Эндпоинт удаления товара',
    tags=['Product'],
    responses={
        204: OpenApiResponse(description='Товар успешно удалён'),
        404: OpenApiResponse(description='Товар не найден'),
        403: OpenApiResponse(description='Нет прав на удаление товара'),
    }
)
class DeleteProductView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, product_id):
        company = request.user.company
        if not company:
            raise PermissionDenied("Пользователь не принадлежит компании")
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Товар не найден'}, status=status.HTTP_404_NOT_FOUND)
        
        if product.storage.company != company:
            raise PermissionDenied("Только сотрудник компании может удалить товар")

        product.delete()
        return Response({'message': 'Товар успешно удалён'}, status=status.HTTP_204_NO_CONTENT)


