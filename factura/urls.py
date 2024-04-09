from django.urls import path
from .views import factura_list, factura_create, factura_update, factura_delete

urlpatterns = [
    path('facturas/listar/', factura_list, name='factura_list'),
    path('facturas/crear/', factura_create, name='factura_create'),
    path('facturas/actualizar/<str:pk>/', factura_update, name='factura_update'),
    path('facturas/eliminar/<str:pk>/', factura_delete, name='factura_delete'),
]

