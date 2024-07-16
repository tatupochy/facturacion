from django.db import models
from proveedor.models import Proveedor
from producto.models import Producto
from factura.models import Factura

# Create your models here.

class Compra(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT)
    cantidad = models.IntegerField()
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    factura = models.ForeignKey(Factura, on_delete=models.PROTECT, null=True, blank=True)
