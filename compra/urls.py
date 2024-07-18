from django.urls import path
from .views import compra_list, generar_reporte


urlpatterns = [
    path('compras/listar/', compra_list, name='compra_list'),
    path('compras/reporte/', generar_reporte, name='generar_reporte'),
]