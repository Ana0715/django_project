from django.urls import path
from .views import CreateSupplierView, GetSupplierView, GetSuppliersListView, UpdateSupplierView, DeleteSupplierView


urlpatterns = [
    path('create/', CreateSupplierView.as_view(), name='create-supplier'),
    path('list/', GetSuppliersListView.as_view(), name='list-suppliers'),
    path('get/<int:supplier_id>', GetSupplierView.as_view(), name='get-supplier'),
    path('update/<int:supplier_id>', UpdateSupplierView.as_view(), name='update-supplier'),
    path('delete/<int:supplier_id>', DeleteSupplierView.as_view(), name='delete-supplier'),
]

