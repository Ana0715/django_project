from django.shortcuts import render
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiRequest, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .serializers import SaleSerializer
from .models import Sale
from product.models import Product
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework import status, generics, pagination
from django.db import transaction
from datetime import datetime


class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@extend_schema(
    description='Эндпоинт создания продажи',
    tags=['Sale'],
    request=OpenApiRequest(
        request={
            'type': 'object',
            'properties': {
                'buyer_name': {
                    'type': 'string',
                    'example': 'Иванов Иван'
                },
                'sale_date': {
                    'type': 'string', 
                    'format': 'date', 
                    'example': '2026-06-06'
                },
                'products': {
                    'type': 'array',
                    'minItems': 1,
                    'items': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer', 'example': 1},
                            'quantity': {'type': 'integer', 'example': 10}
                        },
                        'required': ['id', 'quantity']
                    }
                }
            },
            'required': ['buyer_name', 'products']
        }
    ),
    responses={
        201: OpenApiResponse(response=SaleSerializer, description='Поставка успешно создана'),
        400: OpenApiResponse(description='Неверные данные или ошибка валидации'),
        403: OpenApiResponse(description='Нет прав на создание поставки'),
        404: OpenApiResponse(description='Поставщик или товар не найдены')        
    }
)
class CreateSaleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        company = request.user.company
        if not company:
            return Response({'detail': 'Пользователь не принадлежит ни одной компании'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = SaleSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            sale = serializer.save(company=company)
            response_serializer = SaleSerializer(sale)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    description='Эндпоинт получения списка всех продаж',
    tags=['Sale'],
    parameters=[
        OpenApiParameter(name='start_date', description='Начало периода (YYYY-MM-DD)', required=False, type=OpenApiTypes.DATE, location=OpenApiParameter.QUERY,),
        OpenApiParameter(name='end_date', description='Конец периода (YYYY-MM-DD)', required=False, type=OpenApiTypes.DATE, location=OpenApiParameter.QUERY,),
    ],
    responses={
        200: OpenApiResponse(response=SaleSerializer(many=True), description='Список продаж'),
        403: OpenApiResponse(description='Пользователь не принадлежит компании')
    }
)
class GetSalesListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SaleSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        company = self.request.user.company
        if not company:
            raise PermissionDenied('Пользователь не принадлежит компании')
        
        queryset = Sale.objects.filter(company=company).prefetch_related('sale_products__product').order_by('-sale_date')

        start_date_str = self.request.query_params.get('start_date')
        end_date_str = self.request.query_params.get('end_date')

        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                queryset = queryset.filter(sale_date__gte=start_date)
            except ValueError:
                raise ValidationError('Неверный формат даты start_date')
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                queryset = queryset.filter(sale_date__lte=end_date)
            except ValueError:
                raise ValidationError('Неверный формат даты end_date')

        return queryset


@extend_schema(
    description='Эндпоинт получения информации о поставке',
    tags=['Sale'],
    responses={
        200: OpenApiResponse(response=SaleSerializer, description='Данные о продаже'),
        404: OpenApiResponse(description='Продажа не найдена'),
        403: OpenApiResponse(description='Нет доступа к поставке')
    }
)
class GetSaleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, sale_id):
        company = request.user.company
        if not company:
            raise PermissionDenied('Пользователь не принадлежит компании')
        
        try:
            sale = Sale.objects.prefetch_related('sale_products__product').get(id=sale_id, company=company)
            serializer = SaleSerializer(sale)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Sale.DoesNotExist:
            return Response({'error': 'Поставка не найдена'}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(
    description='Эндпоинт редактирования продажи (можно изменить только buyer_name и sale_date)',
    tags=['Sale'],
    request=OpenApiRequest(
        request={
            'type': 'object',
            'properties': {
                'buyer_name': {
                    'type': 'string',
                    'example': 'Иванов Иван'
                },
                'sale_date': {
                    'type': 'string',
                    'format': 'date',
                    'example': '2026-06-06'
                }
            },
        }
    ),
    responses={
        200: OpenApiResponse(response=SaleSerializer, description='Продажа успешно обновлена'),
        400: OpenApiResponse(description='Неверные данные или ошибка валидации'),
        404: OpenApiResponse(description='Продажа не найдена'),
        403: OpenApiResponse(description='Нет прав на редактирование продажи')
    }
)
class UpdateSaleView(APIView):  
    permission_classes = [IsAuthenticated]

    def put(self, request, sale_id):
        company = request.user.company
        if not company:
            return Response({'error': 'Пользователь не принадлежит компании'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            sale = Sale.objects.get(id=sale_id)
        except Sale.DoesNotExist:
            return Response({'error': 'Продажа не найдена'}, status=status.HTTP_404_NOT_FOUND)
        
        if sale.company != company:
            return Response({'error': 'Нет прав на редактирование этой продажи'}, status=status.HTTP_403_FORBIDDEN)
        
        data = {}
        if 'buyer_name' in request.data:
            data['buyer_name'] = request.data['buyer_name']
        if 'sale_date' in request.data:
            data['sale_date'] = request.data['sale_date']

        if not data:
            return Response({'error': 'Не переданы поля для обновления (buyer_name или sale_date)'}, status=status.HTTP_400_BAD_REQUEST)
        

        serializer = SaleSerializer(instance=sale, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    description='Эндпоинт удаления продажи. При удалении количество товаров возвращается на склад.',
    tags=['Sale'],
    responses={
        204: OpenApiResponse(description='Продажа успешно удалена, товары возвращены на склад'),
        404: OpenApiResponse(description='Продажа не найдена'),
        403: OpenApiResponse(description='Нет прав на удаление')
    }
)
class DeleteSaleView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def delete(self, request, sale_id):
        company = request.user.company
        if not company:
            return Response({'error': 'Пользователь не принадлежит компании'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            sale = Sale.objects.select_for_update().get(id=sale_id)
        except Sale.DoesNotExist:
            return Response({'error': 'Продажа не найдена'}, status=status.HTTP_404_NOT_FOUND)
        
        if company != sale.company:
            return Response({'error': 'Нет прав на удаление продажи'}, status=status.HTTP_403_FORBIDDEN)
        
        product_sales = list(sale.sale_products.select_related('product').all())

        if not product_sales:
            sale.delete()
            return Response({'message': 'Продажа успешно удалена'}, status=status.HTTP_204_NO_CONTENT)
          
        products_to_delete = []
        for ps in product_sales:
            product = ps.product
            product.quantity += ps.quantity
            products_to_delete.append(product)

        Product.objects.bulk_update(products_to_delete, ['quantity'])

        sale.delete()
        
        return Response({'message': 'Продажа успешно удалена, товары возвращены на склад'}, status=status.HTTP_204_NO_CONTENT)


