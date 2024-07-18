from django.urls import path
from .views import venta_list, generar_reporte


urlpatterns = [
    path('ventas/listar/', venta_list, name='venta_list'),
    path('ventas/reporte/', generar_reporte, name='generar_reporte'),
]