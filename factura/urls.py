from django.urls import path
from .views import factura_list, factura_create, factura_update, factura_delete, generar_reporte, factura_detail, factura_filter

urlpatterns = [
    path('facturas/listar/', factura_list, name='factura_list'),
    path('facturas/detalle/<str:pk>/', factura_detail, name='factura_detail'),
    path('facturas/crear/', factura_create, name='factura_create'),
    path('facturas/actualizar/<str:pk>/', factura_update, name='factura_update'),
    path('facturas/eliminar/<str:pk>/', factura_delete, name='factura_delete'),
    path('facturas/buscar/', factura_filter, name='factura_filter'),
    path('facturas/reporte/', generar_reporte, name='generar_reporte'),
]

