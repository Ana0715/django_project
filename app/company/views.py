from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiRequest, OpenApiResponse
from .serializers import CompanySerializer
from .models import Company
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied


@extend_schema(
    description='Эндпоинт создания компании',
    tags=['Company'],
    request=OpenApiRequest(
        request={
            'type': 'object',
            'properties': {
                'inn': {
                    'type': 'string',
                    'example': '1234567890'
                    },
                'company_name': {
                    'type': 'string',
                    'example': 'ООО Компания'
                    },
            }
        }
    ),
    responses={
        201: OpenApiResponse(response=CompanySerializer, description='Компания успешно создана'),
        400: OpenApiResponse(description='Компания с этим ИНН уже существует'),
        403: OpenApiResponse(description='Пользователь уже владеет компанией')
    }
)
class CreateCompanyView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        if request.user.is_company_owner:
            return Response(
                {'error': 'Пользователь уже владеет компанией'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = CompanySerializer(data=request.data)
        if serializer.is_valid():
            # Связываем компанию с пользователем
            company = serializer.save(owner=request.user)
            # Обновляем статус пользователя
            request.user.is_company_owner = True
            request.user.company = company
            request.user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
        
@extend_schema(
    description='Эндпоинт получения данных о компании',
    tags=['Company'],
    responses={
        200: OpenApiResponse(response=CompanySerializer, description='Данные компании'),
        404: OpenApiResponse(description='Компания не найдена')
    }
)
class GetCompanyView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, company_id):
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response({'error': 'Компания не найдена'}, status=status.HTTP_404_NOT_FOUND)
                
        serializer = CompanySerializer(company)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    description='Эндпоинт редактирования компании',
    tags=['Company'],
    request=OpenApiRequest(
        request={
            'type': 'object',
            'properties': {
                'inn': {
                    'type': 'string',
                    'example': '1234567890',
                    'required': False
                },
                'company_name': {
                    'type': 'string',
                    'example': 'ООО Компания',
                    'required': False
                }
            }
        }
    ),
    responses={
        200: OpenApiResponse(response=CompanySerializer, description='Компания успешно обновлена'),
        400: OpenApiResponse(description='Неверные данные'),
        404: OpenApiResponse(description='Компания не найдена')
    }
)
class UpdateCompanyView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, company_id):
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response({'error': 'Компания не найдена'}, status=status.HTTP_404_NOT_FOUND)
        
        if request.user != company.owner:
                raise PermissionDenied("Только владелец может редактировать компанию")

        serializer = CompanySerializer(
            company,
            data=request.data,
            partial=False
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    description='Эндпоинт удаления компании',
    tags=['Company'],
    responses={
        204: OpenApiResponse(description='Компания успешно удалена'),
        404: OpenApiResponse(description='Компания не найдена')
    }
)
class DeleteCompanyView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, company_id):
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response({'error': 'Компания не найдена'}, status=status.HTTP_404_NOT_FOUND)

        if request.user != company.owner:
            raise PermissionDenied("Только владелец может удалить компанию")
        
        company.delete()
        request.user.is_company_owner = False
        request.user.company = None
        request.user.save()
        return Response({'message': 'Компания успешно удалена'}, status=status.HTTP_204_NO_CONTENT)
