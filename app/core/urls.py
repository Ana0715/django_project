from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from django.contrib import admin
from django.urls import path, include

from authenticate import views


BASE_API_V1_PREFIX = 'api/v1'


urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('admin/', admin.site.urls),
    path(f'{BASE_API_V1_PREFIX}/authenticate/', include('authenticate.urls')),
    path(f'{BASE_API_V1_PREFIX}/companies/', include('company.urls')),
    path(f'{BASE_API_V1_PREFIX}/storages/', include('storage.urls')),
    path(f'{BASE_API_V1_PREFIX}/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(f'{BASE_API_V1_PREFIX}/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path(f'{BASE_API_V1_PREFIX}/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
