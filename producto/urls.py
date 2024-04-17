from django.urls import path
from .views import producto_create, producto_list, producto_detail, producto_update, producto_delete, generar_reporte


urlpatterns = [
    path('productos/listar/', producto_list, name='producto_list'),
    path('productos/detalle/<str:pk>/', producto_detail, name='producto_detail'),
    path('productos/crear/', producto_create, name='producto_create'),
    path('productos/actualizar/<str:pk>/', producto_update, name='producto_update'),
    path('productos/eliminar/<str:pk>/', producto_delete, name='producto_delete'),
    path('productos/reporte/', generar_reporte, name='generar_reporte'),
]