from django.db import models
from cliente.models import Cliente
from proveedor.models import Proveedor
from producto.models import Producto

# Create your models here.


class Factura(models.Model):
    numero = models.CharField(max_length=100, editable=False, unique=True)
    numeracion = models.CharField(max_length=100, editable=False, unique=True, null=True)
    fecha_emision = models.DateField(editable=False)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, blank=True, null=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, blank=True, null=True)
    sub_total = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    establecimiento = models.CharField(max_length=100, editable=False)
    punto_expedicion = models.CharField(max_length=100, editable=False)
    fecha_vencimiento = models.DateField(blank=True, null=True)
    timbrado = models.CharField(max_length=100)
    condicion_venta = models.CharField(choices=(
                                                    ('contado', 'Contado'),
                                                    ('credito', 'Crédito'),
                                                ), max_length=100)
    operacion = models.CharField(
        choices=(
            ('compra', 'Compra'),
            ('venta', 'Venta')
        ), max_length=100, blank=True, null=True
    )
    total_iva_5 = models.DecimalField(max_digits=10, decimal_places=2)
    sub_total_iva_5 = models.DecimalField(max_digits=10, decimal_places=2)
    total_iva_10 = models.DecimalField(max_digits=10, decimal_places=2)
    sub_total_iva_10 = models.DecimalField(max_digits=10, decimal_places=2)
    total_iva = models.DecimalField(max_digits=10, decimal_places=2)
    sub_total_iva = models.DecimalField(max_digits=10, decimal_places=2)


class ItemFactura(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    iva_exenta = models.DecimalField(max_digits=10, decimal_places=2)
    iva_5 = models.DecimalField(max_digits=10, decimal_places=2)
    iva_10 = models.DecimalField(max_digits=10, decimal_places=2)


class UltimoNumeroFactura(models.Model):
    ultimo_numero = models.PositiveIntegerField()

