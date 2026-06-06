from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiRequest, OpenApiResponse
from .serializers import SupplySerializer
from .models import Supply
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

    
@extend_schema(
    description='Эндпоинт получения списка поставок компании',
    tags=['Supply'],
    responses={
        200: OpenApiResponse(response=SupplySerializer(many=True), description='Список поставок'),
        403: OpenApiResponse(description='Пользователь не принадлежит компании'),
    }
)
class GetSuppliesListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        company = request.user.company
        if not company:
            raise PermissionDenied("Пользователь не принадлежит компании")
        
        # company = getattr(request.user, 'company', None)
        # if not company:
        #     raise PermissionDenied("Пользователь не принадлежит ни одной компании")

        supplies = Supply.objects.filter(supplier__company=company).select_related('supplier').prefetch_related('supply_products__product')
        serializer = SupplySerializer(supplies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    description='Эндпоинт создания поставки',
    tags=['Supply'],
    request=OpenApiRequest(
        request={
            'type': 'object',
            'properties': {
                'supplier_id': {
                    'type': 'integer',
                    'example': 1,
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
            'required': ['supplier_id', 'products']
        }
    ),
    responses={
        201: OpenApiResponse(response=SupplySerializer, description='Поставка успешно создана'),
        400: OpenApiResponse(description='Неверные данные или ошибка валидации'),
        403: OpenApiResponse(description='Нет прав на создание поставки'),
        404: OpenApiResponse(description='Поставщик или товар не найдены')
    }
)
class CreateSupplyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # if not getattr(request.user, 'company', None):
        if not request.user.company:
            return Response({'detail': 'Пользователь не принадлежит ни одной компании'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = SupplySerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                supply = serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'detail': f'Произошла ошибка при создании поставки: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    description='Эндпоинт получения информации о поставке',
    tags=['Supply'],
    responses={
        200: OpenApiResponse(response=SupplySerializer, description='Данные о поставке'),
        404: OpenApiResponse(description='Поставка не найдена'),
        403: OpenApiResponse(description='Нет доступа к поставке')
    }
)
class GetSupplyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, supply_id):
        # company = getattr(request.user, 'company', None)
        company = request.user.company
        if not company:
            raise PermissionDenied("Пользователь не принадлежит компании")

        try:
            supply = Supply.objects.select_related('supplier').prefetch_related('supply_products__product').get(id=supply_id, supplier__company=company)
            serializer = SupplySerializer(supply)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Supply.DoesNotExist:
            return Response({'error': 'Поставка не найдена'}, status=status.HTTP_404_NOT_FOUND)




