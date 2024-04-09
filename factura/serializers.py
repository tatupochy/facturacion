from rest_framework import serializers
from datetime import datetime
from .models import Factura, ItemFactura


class ItemFacturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemFactura
        fields = '__all__'

class FacturaSerializer(serializers.ModelSerializer):
    items = ItemFacturaSerializer(source='itemfactura_set', many=True, read_only=True)  # Campo para incluir los items de la factura

    class Meta:
        model = Factura
        fields = '__all__'
        extra_kwargs = {
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