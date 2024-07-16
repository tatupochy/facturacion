from rest_framework import serializers
from .models import Compra

from producto.serializers import ProductoSerializer
from proveedor.serializers import ProveedorSerializer
from factura.serializers import FacturaSerializer

class CompraSerializer(serializers.ModelSerializer):
    proveedor = ProveedorSerializer()
    producto = ProductoSerializer()
    factura = FacturaSerializer()

    class Meta:
        model = Compra
        fields = '__all__'

    depth = 1