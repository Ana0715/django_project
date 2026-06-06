from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('add-employee/', views.AddEmployeeView.as_view(), name='add-employee'),
    path('take-token/', views.TakeToken.as_view(), name='take-token'),
]