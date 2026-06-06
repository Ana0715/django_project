from django.urls import path
from .views import CreateSupplyView, GetSuppliesListView, GetSupplyView


urlpatterns = [
    path('create/', CreateSupplyView.as_view(), name='create-supply'),
    path('list/', GetSuppliesListView.as_view(), name='list-supplies'),
    path('get/<int:supply_id>/', GetSupplyView.as_view(), name='get-supply'),
]


