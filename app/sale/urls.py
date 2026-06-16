from django.urls import path
from . import views


urlpatterns = [
    path('create/', views.CreateSaleView.as_view(), name='create-sale'),
    path('list/', views.GetSalesListView.as_view(), name='list-sales'),
    path('get/<int:sale_id>', views.GetSaleView.as_view(), name='get-sale'),
    path('update/<int:sale_id>', views.UpdateSaleView.as_view(), name='update-sale'),
    path('delete/<int:sale_id>', views.DeleteSaleView.as_view(), name='delete-sale'),
]

