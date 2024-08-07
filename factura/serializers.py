from rest_framework import serializers
from datetime import datetime

from producto.serializers import ProductoSerializer
from .models import Factura, ItemFactura


class ItemFacturaSerializer(serializers.ModelSerializer):

    producto = ProductoSerializer()
    
    class Meta:
        model = ItemFactura
        fields = '__all__'
        

class FacturaSerializer(serializers.ModelSerializer):
    items = ItemFacturaSerializer(source='itemfactura_set', many=True, read_only=True)  # Campo para incluir los items de la factura

    class Meta:
        model = Factura
        fields = '__all__'
        extra_kwargs = {
            'operacion': {'choices': ['venta', 'compra']},
            'condicion_venta': {'choices': ['contado', 'credito']},
            'sub_total': {'required': False},
            'total': {'required': False},
            'total_iva_5': {'required': False},
            'sub_total_iva_5': {'required': False},
            'total_iva_10': {'required': False},
            'sub_total_iva_10': {'required': False},
            'total_iva': {'required': False},
            'sub_total_iva': {'required': False},
        }
        depth = 1


class FilterSerializer(serializers.Serializer):
    operacion = serializers.ChoiceField(choices=['venta', 'compra'], required=True)
    fecha_emision = serializers.DateField(required=False)

    def validate_fecha_emision(self, value):
        if value:
            if value > datetime.now().date():
                raise serializers.ValidationError('La fecha de emisión no puede ser mayor a la fecha actual')
        return value
    
    def validate(self, data):
        if not data.get('fecha_emision'):
            raise serializers.ValidationError('Debe ingresar la fecha de emisión')
        return data
    