from django.urls import path
from .views import proveedor_create, proveedor_list, proveedor_detail, proveedor_update, proveedor_delete

urlpatterns = [
    path('proveedores/listar/', proveedor_list, name='proveedor_list'),
    path('proveedores/crear/', proveedor_create, name='proveedor_create'),
    path('proveedores/actualizar/<str:pk>/', proveedor_update, name='proveedor_update'),
    path('proveedores/eliminar/<str:pk>/', proveedor_delete, name='proveedor_delete'),
]