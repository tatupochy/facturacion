from django.db import models

# Create your models here.


class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock = models.IntegerField(default=1)
    iva = models.CharField(max_length=10, choices=[('0', '0%'), ('5', '5%'), ('10', '10%')], default='10')
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre