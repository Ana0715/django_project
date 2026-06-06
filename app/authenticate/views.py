from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiRequest, OpenApiResponse, OpenApiExample
from .serializers import UserSerializer, LoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .models import User
from rest_framework.exceptions import PermissionDenied
from company.models import Company


def home_page(request):
    return render(request, 'authenticate/base.html')


@extend_schema(
    description='Эндпоинт регистрации пользователя',
    tags=['User'],
    request=UserSerializer,
    responses={
        201: OpenApiResponse(
            response={
                'type': 'object',
                'properties': {
                    'refresh': {
                        'type': 'string',
                        'description': 'Refresh токен для обновления access токена'
                    },
                    'access': {
                        'type': 'string',
                        'description': 'Access токен для авторизации'
                    },
                    'user': {
                        'type': 'object',
                        'properties': {
                            'username': {
                                'type': 'string', 
                                },
                            'email': {
                                'type': 'string', 
                                'format': 'email', 
                                }
                        }
                    }
                }
            },
            description='Пользователь успешно создан',
        ),
        400: OpenApiResponse(
            response={
                'type': 'object',
                'properties': {
                    'field_name': {
                        'type': 'array',
                        'items': {'type': 'string'}
                    }
                }
            },
            description='Ошибка валидации данных'
        )
    },
    examples=[
        OpenApiExample(
            'Пример регистрации',
            summary='Пример данных для регистрации',
            value={
                'username': 'JohnDoe',
                'email': 'john@example.com',
                'password': 'securepassword123'
            }
        )
    ]
)
class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    description='Эндпоинт авторизации пользователя (логин)',
    tags=['api'],
    request=LoginSerializer,
    responses={
        200: OpenApiResponse(
            response={
                'type': 'object',
                'properties': {
                    'refresh': {
                        'type': 'string',
                        'description': 'Refresh токен'
                    },
                    'access': {
                        'type': 'string',
                        'description': 'Access токен'
                    },
                    'user': {
                        'type': 'object',
                        'properties': {
                            'username': {
                                'type': 'string', 
                                },
                            'email': {
                                'type': 'string', 
                                'format': 'email', 
                                },
                        }
                    }
                }
            },
            description='Успешная авторизация'
        ),
        400: OpenApiResponse(
            response={
                'type': 'object',
                'properties': {
                    'detail': {'type': 'string'},
                    'email': {'type': 'array'},
                    'password': {'type': 'array'}
                }
            },
            description='Неверные учётные данные или ошибка валидации'
        )
    },
    examples=[
        OpenApiExample(
            'Пример логина',
            summary='Пример данных для авторизации',
            value={
                'email': 'john@example.com',
                'password': 'securepassword123'
            }
        )
    ]
)
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context = {'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'is_company_owner': user.is_company_owner,
                    'is_admin': user.is_admin
                }
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    description='Эндпоинт получения токена',
    tags=['api'],
    responses={
        200: OpenApiResponse(
            response={
                'type': 'object',
                'properties': {
                    'refresh': {
                        'type': 'string',
                        'description': 'Refresh токен'
                    },
                    'access': {
                        'type': 'string',
                        'description': 'Access токен'
                    },
                }
            },
            description='Токен успешно получен'
        ),
        401: OpenApiResponse(
            response={
                'type': 'object',
                'properties': {
                    'detail': {'type': 'string'},                }
            },
            description='Пользователь не авторизован'
        )
    },
)
class TakeToken(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f'Ошибка при генерации токена: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    description='Эндпоинт добавления сотрудника в компанию',
    tags=['User'],
    request=OpenApiRequest(
        request={
            'type': 'object',
            'properties': {
                'email': {
                    'type': 'string',
                    'format': 'email',
                    'example': 'employee@example.com'
                }
            }
        }
    ),
    responses={
        200: OpenApiResponse(description='Сотрудник успешно добавлен'),
        400: OpenApiResponse(description='Неверные данные'),
        403: OpenApiResponse(description='Нет прав на добавление сотрудников'),
        404: OpenApiResponse(description='Пользователь не найден'),
        409: OpenApiResponse(description='Пользователь уже принадлежит другой компанией')
    }
)
class AddEmployeeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.is_company_owner:
            return Response({'error': 'Только владелец компании может добавлять сотрудников'}, status=status.HTTP_403_FORBIDDEN)
        
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email сотрудника обязателен'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            employee = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь с таким email не найден'}, status=status.HTTP_404_NOT_FOUND)
        
        if employee.company and employee.company != request.user.company:
            return Response({'error': 'Пользователь уже принадлежит другой компании'}, status=status.HTTP_409_CONFLICT)
        
        if employee.company:
            return Response({'error': 'Пользователь уже является сотрудником компании'}, status=status.HTTP_409_CONFLICT)
        
        employee.company = request.user.company
        employee.save()
        return Response({'message': 'Сотрудник успешно добавлен в компанию'}, status=status.HTTP_200_OK)





























# @extend_schema(
#     description='Эндпоинт создания товара',
#     tags=['Products'],
#     request=OpenApiRequest(
#         request={
#             'type': 'object',
#             'properties': {
#                 'title': {
#                     'type': 'string',
#                     'example': 'Клавиатура'
#                     },
#                 'purchase_price': {
#                     'type': 'string',
#                     'example': '1200.25'
#                     },
#                 'sale_price': {
#                     'type': 'string',
#                     'example': '2500.00'
#                     },
#                 'quantity': {
#                     'type': 'integer',
#                     'example': 10
#                     },
#                 'storage': {
#                     'type': 'integer',
#                     'example': 10
#                     },
#             }
#         }
#     )
# )
# class CreateProductView(APIView):
#     def post(self, request):
#         serializer = ProductSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)