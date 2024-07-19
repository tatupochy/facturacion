from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from response import create_response
from django.db import transaction
from decimal import Decimal
from .serializers import FacturaSerializer
from .models import Factura, ItemFactura, UltimoNumeroFactura
from producto.models import Producto
from cliente.models import Cliente
from compra.models import Compra
from proveedor.models import Proveedor
from venta.models import Venta
from io import BytesIO
import base64
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


# Create your views here.

@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def factura_create(request):
    serializer = FacturaSerializer(data=request.data)
    if serializer.is_valid():
        with transaction.atomic():
            
            operacion = request.data.get('operacion')

            cliente = None
            proveedor = None

            if operacion == 'venta':
                cliente_data = request.data.get('cliente')
                cliente_id = cliente_data.get('id')
                try:
                    cliente = Cliente.objects.get(pk=cliente_id)
                except Cliente.DoesNotExist:
                    response = create_response('error', 400, f"Cliente con ID {cliente_id} no encontrado.")
                    return Response(response, status=400)
            elif operacion == 'compra':
                proveedor_data = request.data.get('proveedor')
                proveedor_id = proveedor_data.get('id')
                try:
                    proveedor = Proveedor.objects.get(pk=proveedor_id)
                except Proveedor.DoesNotExist:
                    response = create_response('error', 400, f"Proveedor con ID {proveedor_id} no encontrado.")
                    return Response(response, status=400)

            # Lógica para generar campos como numero, numeracion, establecimiento, punto_expedicion, etc.
            ultimo_numero = UltimoNumeroFactura.objects.first()
            if ultimo_numero is None:
                ultimo_numero = UltimoNumeroFactura.objects.create(ultimo_numero=0)
            numero = ultimo_numero.ultimo_numero + 1
            ultimo_numero.ultimo_numero = numero

            print(ultimo_numero.ultimo_numero)

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
                proveedor=proveedor,
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
                producto_data = item_data.get('producto')
                producto_id = producto_data.get('id')
                cantidad = item_data.get('cantidad')
                
                try:
                    producto = Producto.objects.get(pk=producto_id)
                except Producto.DoesNotExist:
                    response = create_response('error', 400, f"Producto con ID {producto_id} no encontrado.")
                    return Response(response, status=400)

                if operacion == 'venta':
                    precio_unitario = producto.precio
                elif operacion == 'compra':
                    precio_unitario = producto.costo

                total = precio_unitario * cantidad
                sub_total += total

                # Cálculo del IVA y otros campos según la tasa de IVA del producto

                if producto.iva == '5':
                    total_iva_5 += total * Decimal(0.05)
                    sub_total_iva_5 += total 
                elif producto.iva == '10':
                    total_iva_10 += total * Decimal(0.1)
                    sub_total_iva_10 += total 

                if operacion == 'compra':
                    Compra.objects.create(
                        proveedor=proveedor,
                        cantidad=cantidad,
                        producto=producto,
                        factura=factura
                    )

                    producto.stock += cantidad
                    producto.save()

                elif operacion == 'venta':
                    Venta.objects.create(
                        cliente=cliente,
                        cantidad=cantidad,
                        producto=producto,
                        factura=factura
                    )

                    producto.stock -= cantidad
                    producto.save()

                # Crear el ítem de la factura
                ItemFactura.objects.create(
                    factura=factura,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=precio_unitario,
                    iva_exenta=total if producto.iva == '0' else 0,
                    iva_5=total_iva_5,
                    iva_10=total_iva_10
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

            ultimo_numero.save()

            response = create_response('success', 201, "Factura creada correctamente.", serializer.data)
            return Response(response, status=201)
    
    return Response(serializer.errors)


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def factura_list(request):
    facturas = Factura.objects.all()
    serializer = FacturaSerializer(facturas, many=True)

    response = create_response('success', 200, "Lista de facturas obtenida correctamente.", serializer.data)
    return Response(response)


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def factura_detail(request, pk):
    try:
        factura = Factura.objects.get(pk=pk)
    except Factura.DoesNotExist:
        response = create_response('error', 404, f"Factura con ID {pk} no encontrada.")
        return Response(response, status=404)

    serializer = FacturaSerializer(factura)

    response = create_response('success', 200, "Factura obtenida correctamente.", serializer.data)
    return Response(response)

@api_view(['POST'])
def factura_filter(request):
    operacion = request.data.get('operacion')
    fecha_emision = request.data.get('fecha_emision')

    print('--------------------')
    print('FILTRANDO')
    print(request)
    print(request.data)
    print(operacion)
    print(fecha_emision)
    print('--------------------')

    if fecha_emision is not None:
        if operacion == 'venta':
            facturas = Factura.objects.filter(operacion='venta', fecha_emision=fecha_emision)
        elif operacion == 'compra':
            facturas = Factura.objects.filter(operacion='compra', fecha_emision=fecha_emision)
    else:
        print('No hay fecha de emisión')
        if operacion == 'venta':
            facturas = Factura.objects.filter(operacion='venta')
        elif operacion == 'compra':
            facturas = Factura.objects.filter(operacion='compra')

    serializer = FacturaSerializer(facturas, many=True)

    response = create_response('success', 200, "Lista de facturas filtrada correctamente.", serializer.data)
    return Response(response)

@api_view(['PUT'])
# @permission_classes([IsAuthenticated])
def factura_update(request, pk):
    serializer = FacturaSerializer(data=request.data)
    if serializer.is_valid():
        with transaction.atomic():
            factura_id = request.data.get('id')  # Obtener el ID de la factura
            if factura_id:
                try:
                    factura = Factura.objects.get(pk=factura_id)
                except Factura.DoesNotExist:

                    response = create_response('error', 404, f"Factura con ID {factura_id} no encontrada.")
                    return Response(response, status=404)
            else:
                response = create_response('error', 400, "No se proporcionó el ID de la factura.")
                return Response(response, status=400)

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
                    response = create_response('error', 404, f"Producto con ID {producto_id} no encontrado.")
                    return Response(response, status=404) 

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
                item_id = item_data.get('producto')  # Obtener el ID del ítem si está presente
                if item_id:
                    try:
                        item = ItemFactura.objects.get(producto=producto, factura=factura)
                        item.producto = producto
                        item.cantidad = cantidad
                        item.precio_unitario = precio_unitario
                        item.iva_exenta = total if producto.iva == '0' else 0
                        item.iva_5 = total if producto.iva == '5' else 0
                        item.iva_10 = total if producto.iva == '10' else 0
                        item.save()
                    except ItemFactura.DoesNotExist:
                        response = create_response('error', 404, f"Ítem con ID {item_id} no encontrado.")
                        return Response(response, status=404)
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

            # obtener la factura actualizada
            factura = Factura.objects.get(pk=factura_id)
            serializer = FacturaSerializer(factura)

            response = create_response('success', 200, "Factura actualizada correctamente.", serializer.data)
            return Response(response, status=200)
    
    response = create_response('error', 400, "Error al actualizar la factura.", serializer.errors)
    return Response(response, status=400)


@api_view(['DELETE'])
# @permission_classes([IsAuthenticated])
def factura_delete(request, pk):
    try:
        factura = Factura.objects.get(pk=pk)
    except Factura.DoesNotExist:
        response = create_response('error', 404, f"Factura con ID {pk} no encontrada.")
        return Response(response, status=404)

    # Eliminar los ítems de la factura
    items = ItemFactura.objects.filter(factura=factura)
    items.delete()

    # Eliminar la factura
    factura.delete()

    response = create_response('success', 204, f"Factura con ID {pk} eliminada correctamente.")
    return Response(response, status=204)


@api_view(['GET'])
def generar_reporte(request):

    facturas = Factura.objects.all()

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.drawString(100, 750, 'Reporte de facturas')
    y = 700
    for factura in facturas:
        y -= 20
        c.drawString(100, y, f'Número: {factura.numeracion}')
        y -= 20
        c.drawString(100, y, f'Cliente: {factura.cliente.nombre}')
        y -= 20
        c.drawString(100, y, f'Fecha de emisión: {factura.fecha_emision}')
        y -= 20
        c.drawString(100, y, f'Total: {factura.total}')
        y -= 20
        c.drawString(100, y, f'Total IVA 5%: {factura.total_iva_5}')
        y -= 20
        c.drawString(100, y, f'Total IVA 10%: {factura.total_iva_10}')
        y -= 20
        c.drawString(100, y, f'Total IVA: {factura.total_iva}')
        y -= 20
        c.drawString(100, y, f'Subtotal: {factura.sub_total}')
        y -= 20
        c.drawString(100, y, f'Subtotal IVA: {factura.sub_total_iva}')
        y -= 20
        c.drawString(100, y, f'Subtotal IVA 5%: {factura.sub_total_iva_5}')
        y -= 20
        c.drawString(100, y, f'Subtotal IVA 10%: {factura.sub_total_iva_10}')
        y -= 20
        c.drawString(100, y, 'Ítems:')
        y -= 20
        items = ItemFactura.objects.filter(factura=factura)
        for item in items:
            c.drawString(120, y, f'{item.producto.nombre} - Cantidad: {item.cantidad} - Precio unitario: {item.precio_unitario}')
            y -= 20
    c.save()

    pdf = buffer.getvalue()
    base64_pdf = base64.b64encode(pdf).decode('utf-8')

    response = create_response('success', 200, "Reporte de facturas generado correctamente.", base64_pdf)
    return Response(response, status=200)

