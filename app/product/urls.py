from django.urls import path
from .views import CreateProductView, GetProductView, GetProductsListView, UpdateProductView, DeleteProductView


urlpatterns = [
    path('create/', CreateProductView.as_view(), name='create-product'),
    path('list/', GetProductsListView.as_view(), name='list-products'),
    path('get/<int:product_id>', GetProductView.as_view(), name='get-product'),
    path('update/<int:product_id>', UpdateProductView.as_view(), name='update-product'),
    path('delete/<int:product_id>', DeleteProductView.as_view(), name='delete-product'),
]