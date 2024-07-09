from django.db import models
from proveedor.models import Proveedor
from producto.models import Producto

# Create your models here.

class Compra:
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT)
    cantidad = models.IntegerField()
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
