from django.urls import path
from .views import compra_list


urlpatterns = [
    path('compras/listar/', compra_list, name='compra_list'),
]