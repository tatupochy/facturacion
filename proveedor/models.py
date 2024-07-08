from django.db import models

# Create your models here.


class Proveedor(models.Model):
    nombre = models.CharField(max_length=50)
    direccion = models.CharField(max_length=50)
    telefono = models.CharField(max_length=50)
    email = models.EmailField()
    ruc = models.CharField(max_length=50)
    activo = models.BooleanField(default=True)
    pais = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre