from django.urls import path, include
from .views import CreateStorageView, GetStorageView, UpdateStorageView, DeleteStorageView


urlpatterns = [
    path('create/', CreateStorageView.as_view(), name='create-storage'),
    path('get/<int:storage_id>', GetStorageView.as_view(), name='get-storage'),
    path('update/<int:storage_id>', UpdateStorageView.as_view(), name='update-storage'),
    path('delete/<int:storage_id>', DeleteStorageView.as_view(), name='delete-storage'),
]