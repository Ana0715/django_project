from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiRequest, OpenApiResponse
from .serializers import SupplierSerializer
from .models import Supplier
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied


@extend_schema(
    description='Эндпоинт создания поставщика',
    tags=['Supplier'],
    request=OpenApiRequest(
        request={
            'type': 'object',
            'properties': {
                'inn': {
                    'type': 'string',
                    'example': '1234567890'
                },
                'title': {
                    'type': 'string',
                    'example': 'Поставщик'
                },
            }
        }
    ),
    responses={
        201: OpenApiResponse(response=SupplierSerializer, description='Поставщик успешно создан'),
        400: OpenApiResponse(description='Неверные данные или ошибка валидации'),
        403: OpenApiResponse(description='Нет прав на создание склада'),
    }
)
class CreateSupplierView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        company = request.user.company

        if not company:
            raise PermissionDenied("Только сотрудник компании может создать поставщика")
        
        serializer = SupplierSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(company=company)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    description='Эндпоинт получения списка поставщиков компании',
    tags=['Supplier'],
    responses={
        200: OpenApiResponse(response=SupplierSerializer(many=True), description='Список поставщиков'),
        403: OpenApiResponse(description='Нет доступа к поставщикам')
    }
)
class GetSuppliersListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        company = request.user.company
        if not company:
            raise PermissionDenied("Пользователь не принадлежит компании")

        suppliers = Supplier.objects.filter(company=company)
        serializer = SupplierSerializer(suppliers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    description='Эндпоинт получения информации о поставщике',
    tags=['Supplier'],
    responses={
        200: OpenApiResponse(response=SupplierSerializer, description='Данные о поставщике'),
        404: OpenApiResponse(description='Поставщик не найден'),
        403: OpenApiResponse(description='Нет доступа к постащику')
    }    
)
class GetSupplierView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, supplier_id):
        try:
            supplier = Supplier.objects.get(id=supplier_id)
        except Supplier.DoesNotExist:
            return Response({'error': 'Поставщик не найден'}, status=status.HTTP_404_NOT_FOUND)
            
        if request.user.company != supplier.company:
            raise PermissionDenied("Нет доступа к поставщику")
        
        serializer = SupplierSerializer(supplier)
        return Response(serializer.data, status=status.HTTP_200_OK)  


@extend_schema(
    description='Эндпоинт редактирования поставщика',
    tags=['Supplier'],
    request=OpenApiRequest(
        request={
            'type': 'object',
            'properties': {
                'inn': {
                    'type': 'string',
                    'example': '1234567890',
                    'required': False
                },
                'title': {
                    'type': 'string',
                    'example': 'Поставщик',
                    'required': False
                },
            }
        }
    ),
    responses={
        200: OpenApiResponse(response=SupplierSerializer, description='Поставщик успешно обновлен'),
        400: OpenApiResponse(description='Неверные данные'),
        404: OpenApiResponse( description='Поставщик не найден'),
        403: OpenApiResponse(description='Нет прав на редактирование')
    }
)
class UpdateSupplierView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, supplier_id):
        try:
            supplier = Supplier.objects.get(id=supplier_id)
        except Supplier.DoesNotExist:
            return Response({'error': 'Поставщик не найден'}, status=status.HTTP_404_NOT_FOUND)
            
        if request.user.company != supplier.company:
            raise PermissionDenied("Нет прав на редактирование")

        if 'company' in request.data:
            return Response({'error': 'Изменение company запрещено'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = SupplierSerializer(supplier, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    description='Эндпоинт удаления поставщика',
    tags=['Supplier'],
    responses={
        204: OpenApiResponse(description='Поставщик успешно удалён'),
        404: OpenApiResponse(description='Поставщик не найден'),
        403: OpenApiResponse(description='Нет прав на удаление')
    }
)
class DeleteSupplierView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, supplier_id):
        try:
            supplier = Supplier.objects.get(id=supplier_id)
        except Supplier.DoesNotExist:
            return Response({'error': 'Поставщик не найден'}, status=status.HTTP_404_NOT_FOUND)
        
        if request.user.company != supplier.company:
            return Response({'error': 'Нет прав на удаление'}, status=status.HTTP_403_FORBIDDEN)

        supplier.delete()
        return Response({'message': 'Поставщик успешно удалён'}, status=status.HTTP_204_NO_CONTENT)
