from django.urls import path
from .views import venta_list


urlpatterns = [
    path('ventas/listar/', venta_list, name='venta_list'),
]