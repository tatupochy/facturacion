from django.db import models

# Create your models here.


class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()
    ruc = models.CharField(max_length=20)
    pais = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre