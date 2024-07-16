from django.db import models
from cliente.models import Cliente
from producto.models import Producto
from factura.models import Factura

# Create your models here.

class Venta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    cantidad = models.IntegerField()
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    factura = models.ForeignKey(Factura, on_delete=models.PROTECT, null=True, blank=True)
