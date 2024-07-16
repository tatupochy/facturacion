from rest_framework import serializers
from .models import Venta

from producto.serializers import ProductoSerializer
from cliente.serializers import ClienteSerializer
from factura.serializers import FacturaSerializer

class VentaSerializer(serializers.ModelSerializer):
    cliente = ClienteSerializer()
    producto = ProductoSerializer()
    factura = FacturaSerializer()

    class Meta:
        model = Venta
        fields = '__all__'

    depth = 1