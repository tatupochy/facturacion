from django.db import models
from cliente.models import Cliente
from producto.models import Producto

# Create your models here.

class Compra:
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    cantidad = models.IntegerField()
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
