from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from decimal import Decimal
from .serializers import FacturaSerializer
from .models import Factura, ItemFactura, UltimoNumeroFactura
from producto.models import Producto
from cliente.models import Cliente


# Create your views here.

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def factura_create(request):
    serializer = FacturaSerializer(data=request.data)
    if serializer.is_valid():
        with transaction.atomic():

            cliente_id = request.data.get('cliente')
            try:
                cliente = Cliente.objects.get(pk=cliente_id)
            except Cliente.DoesNotExist:
                return Response({"error": f"Cliente con ID {cliente_id} no encontrado."}, status=400)

            # Lógica para generar campos como numero, numeracion, establecimiento, punto_expedicion, etc.
            ultimo_numero = UltimoNumeroFactura.objects.first()
            if ultimo_numero is None:
                ultimo_numero = UltimoNumeroFactura.objects.create(ultimo_numero=0)
            numero = ultimo_numero.ultimo_numero + 1

            establecimiento = request.data.get('establecimiento')
            punto_expedicion = request.data.get('punto_expedicion')
            fecha_emision = request.data.get('fecha_emision')
            fecha_vencimiento = request.data.get('fecha_vencimiento')
            # Generar la numeración de la factura
            # El numero de factura debe tener 6 dígitos, por lo que se rellena con ceros a la izquierda
            numeracion = f"{establecimiento}-{punto_expedicion}-{numero:06d}"

            total_iva_5 = 0
            total_iva_10 = 0
            sub_total_iva_5 = 0
            sub_total_iva_10 = 0
            total_iva = 0
            sub_total = 0

            # Crear la factura sin total inicialmente
            factura = serializer.save(
                numero=numero,
                numeracion=numeracion,
                establecimiento=establecimiento,
                punto_expedicion=punto_expedicion,
                fecha_emision=fecha_emision,
                fecha_vencimiento=fecha_vencimiento,
                cliente=cliente,
                total=0,
                total_iva_5=0,
                total_iva_10=0,
                total_iva=0,
                sub_total=0,
                sub_total_iva=0,
                sub_total_iva_5=0,
                sub_total_iva_10=0
            )

            # Procesar los ítems de la factura
            items_data = request.data.get('items', [])  # Obtener los datos de los ítems de la solicitud
            for item_data in items_data:
                producto_id = item_data.get('producto')
                cantidad = item_data.get('cantidad')
                
                try:
                    producto = Producto.objects.get(pk=producto_id)
                except Producto.DoesNotExist:
                    return Response({"error": f"Producto con ID {producto_id} no encontrado."}, status=400)

                precio_unitario = producto.precio
                total = precio_unitario * cantidad
                sub_total += total

                # Cálculo del IVA y otros campos según la tasa de IVA del producto

                if producto.iva == '5':
                    total_iva_5 += total * Decimal(0.05)
                    sub_total_iva_5 += total 
                elif producto.iva == '10':
                    total_iva_10 += total * Decimal(0.1)
                    sub_total_iva_10 += total 

                # Crear el ítem de la factura
                ItemFactura.objects.create(
                    factura=factura,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=precio_unitario,
                    iva_exenta=total if producto.iva == '0' else 0,
                    iva_5=total,
                    iva_10=total
                )

            total_iva = total_iva_5 + total_iva_10

            # Actualizar los campos de la factura con los totales calculados
            factura.total = sub_total
            factura.total_iva_5 = total_iva_5
            factura.total_iva_10 = total_iva_10
            factura.total_iva = total_iva
            factura.sub_total = sub_total - total_iva
            factura.sub_total_iva = sub_total_iva_5 + sub_total_iva_10
            factura.sub_total_iva_5 = sub_total_iva_5
            factura.sub_total_iva_10 = sub_total_iva_10
            factura.save()

            # Actualizar el último número de factura
            ultimo_numero.ultimo_numero = numero
            ultimo_numero.save()

            return Response(serializer.data)
    
    return Response(serializer.errors)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def factura_list(request):
    facturas = Factura.objects.all()
    serializer = FacturaSerializer(facturas, many=True)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def factura_update(request):
    serializer = FacturaSerializer(data=request.data)
    if serializer.is_valid():
        with transaction.atomic():
            factura_id = request.data.get('id')  # Obtener el ID de la factura
            if factura_id:
                try:
                    factura = Factura.objects.get(pk=factura_id)
                except Factura.DoesNotExist:
                    return Response({"error": f"Factura con ID {factura_id} no encontrada."}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"error": "No se proporcionó el ID de la factura."}, status=status.HTTP_400_BAD_REQUEST)

            # Restaurar los totales a 0 antes de recalcularlos
            factura.total_iva_5 = 0
            factura.total_iva_10 = 0
            factura.total_iva = 0
            factura.sub_total = 0
            factura.sub_total_iva_5 = 0
            factura.sub_total_iva_10 = 0

            # Procesar los ítems de la factura
            items_data = request.data.get('items', [])  # Obtener los datos de los ítems de la solicitud
            for item_data in items_data:
                producto_id = item_data.get('producto')
                cantidad = item_data.get('cantidad')

                try:
                    producto = Producto.objects.get(pk=producto_id)
                except Producto.DoesNotExist:
                    return Response({"error": f"Producto con ID {producto_id} no encontrado."}, status=status.HTTP_404_NOT_FOUND)

                precio_unitario = producto.precio
                total = precio_unitario * cantidad
                factura.sub_total += total

                # Cálculo del IVA y otros campos según la tasa de IVA del producto
                if producto.iva == '5':
                    factura.total_iva_5 += total * Decimal(0.05)
                    factura.sub_total_iva_5 += total
                elif producto.iva == '10':
                    factura.total_iva_10 += total * Decimal(0.1)
                    factura.sub_total_iva_10 += total

                # Crear o actualizar el ítem de la factura
                item_id = item_data.get('id')  # Obtener el ID del ítem si está presente
                if item_id:
                    try:
                        item = ItemFactura.objects.get(pk=item_id)
                        item.producto = producto
                        item.cantidad = cantidad
                        item.precio_unitario = precio_unitario
                        item.iva_exenta = total if producto.iva == '0' else 0
                        item.iva_5 = total if producto.iva == '5' else 0
                        item.iva_10 = total if producto.iva == '10' else 0
                        item.save()
                    except ItemFactura.DoesNotExist:
                        return Response({"error": f"Ítem con ID {item_id} no encontrado."}, status=status.HTTP_404_NOT_FOUND)
                else:
                    ItemFactura.objects.create(
                        factura=factura,
                        producto=producto,
                        cantidad=cantidad,
                        precio_unitario=precio_unitario,
                        iva_exenta=total if producto.iva == '0' else 0,
                        iva_5=total if producto.iva == '5' else 0,
                        iva_10=total if producto.iva == '10' else 0
                    )

            # Calcular los totales
            factura.total_iva = factura.total_iva_5 + factura.total_iva_10
            factura.sub_total_iva = factura.sub_total_iva_5 + factura.sub_total_iva_10
            factura.total = factura.sub_total + factura.total_iva
            factura.save()

            return Response(serializer.data)
    
    return Response(serializer.errors)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def factura_delete(request, factura_id):
    try:
        factura = Factura.objects.get(pk=factura_id)
    except Factura.DoesNotExist:
        return Response({"error": f"Factura con ID {factura_id} no encontrada."}, status=status.HTTP_404_NOT_FOUND)

    # Eliminar los ítems de la factura
    factura.items.all().delete()

    # Eliminar la factura
    factura.delete()

    return Response({"message": f"Factura con ID {factura_id} eliminada correctamente."}, status=status.HTTP_204_NO_CONTENT)


