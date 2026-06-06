from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiRequest, OpenApiResponse
from .serializers import (StorageSerializer)
from .models import Storage
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied


@extend_schema(
    description='Эндпоинт создания склада',
    tags=['Storage'],
    request=OpenApiRequest(
        request={
            'type': 'object',
            'properties': {
                'address': {
                    'type': 'string',
                    'example': 'Калининград, Московский проспект, 10'
                    },
            }
        }
    ),
    responses={
        201: OpenApiResponse(response=StorageSerializer, description='Склад успешно создан'),
        400: OpenApiResponse(description='Неверные данные или ошибка валидации'),
        403: OpenApiResponse(description='Нет прав на создание склада')
    },
)
class CreateStorageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        company = request.user.company
        if not company:
            return Response({'error': 'Пользователь не является сотрудником компании'}, status=status.HTTP_400_BAD_REQUEST)

        if Storage.objects.filter(company=company).exists():
            return Response({'error': 'Компания уже имеет склад'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = StorageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(company=company)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@extend_schema(
    description='Эндпоинт получения данных о складе',
    tags=['Storage'],
    responses={
        200: OpenApiResponse(response=StorageSerializer, description='Данные склада'),
        404: OpenApiResponse(description='Склад не найден'),
        403: OpenApiResponse(description='Нет доступа к складу')
    }
)
class GetStorageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, storage_id):
        try:
            storage = Storage.objects.get(id=storage_id)
        except Storage.DoesNotExist:
            return Response({'error': 'Склад не найден'}, status=status.HTTP_404_NOT_FOUND)
            
        # Доступ для всех пользователей компании
        if (request.user.company == storage.company or
            request.user.is_staff):
            serializer = StorageSerializer(storage)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            raise PermissionDenied("Нет доступа к складу")


@extend_schema(
    description='Эндпоинт редактирования склада',
    tags=['Storage'],
    request=OpenApiRequest(
        request={
            'type': 'object',
            'properties': {
                'address': {
                    'type': 'string',
                    'example': 'Калининград, Московский проспект, 10',
                    'required': False
                },
            }
        }
    ),
    responses={
        200: OpenApiResponse(response=StorageSerializer, description='Склад успешно обновлен'),
        400: OpenApiResponse(description='Неверные данные'),
        404: OpenApiResponse( description='Склад не найден'),
        403: OpenApiResponse(description='Нет прав на редактирование')
    }
)
class UpdateStorageView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, storage_id):
        try:
            storage = Storage.objects.get(id=storage_id)
        except Storage.DoesNotExist:
            return Response({'error': 'Склад не найден'}, status=status.HTTP_404_NOT_FOUND)
            
        # Только владелец компании может редактировать
        if request.user != storage.company.owner:
            raise PermissionDenied("Только владелец компании может редактировать склад")

        if 'company_id' in request.data:
            return Response({'error': 'Изменение company_id запрещено'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = StorageSerializer(storage, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    description='Эндпоинт удаления склада',
    tags=['Storage'],
    responses={
        204: OpenApiResponse(description='Склад успешно удален'),
        404: OpenApiResponse(description='Склад не найден'),
        403: OpenApiResponse(description='Нет прав на удаление')
    }
)
class DeleteStorageView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, storage_id):
        try:
            storage = Storage.objects.get(id=storage_id)
        except Storage.DoesNotExist:
            return Response({'error': 'Склад не найден'}, status=status.HTTP_404_NOT_FOUND)
        
        # Только владелец компании может удалить склад
        if request.user != storage.company.owner:
            raise PermissionDenied("Только владелец компании может удалить склад")

        storage.delete()
        return Response({'message': 'Склад успешно удалён'}, status=status.HTTP_204_NO_CONTENT)


