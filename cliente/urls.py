from django.urls import path
from .views import cliente_list, cliente_create, cliente_update, cliente_delete

urlpatterns = [
    path('clientes/listar/', cliente_list, name='cliente_list'),
    path('clientes/crear/', cliente_create, name='cliente_create'),
    path('clientes/actualizar/<str:pk>/', cliente_update, name='cliente_update'),
    path('clientes/eliminar/<str:pk>/', cliente_delete, name='cliente_delete'),
]