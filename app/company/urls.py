from django.urls import path
from .views import CreateCompanyView, GetCompanyView, UpdateCompanyView, DeleteCompanyView


urlpatterns = [
    path('create/', CreateCompanyView.as_view(), name='create-company'),
    path('get/<int:company_id>', GetCompanyView.as_view(), name='get-company'),
    path('update/<int:company_id>', UpdateCompanyView.as_view(), name='update-company'),
    path('delete/<int:company_id>', DeleteCompanyView.as_view(), name='delete-company'),
]