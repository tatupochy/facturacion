from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from response import create_response
from .models import Producto
from .serializers import ProductoSerializer
from django.template.loader import get_template
from django.http import HttpResponse
import base64
from io import BytesIO
from xhtml2pdf import pisa
from factura.models import Factura, ItemFactura


# Create your views here.

@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def producto_create(request):
    serializer = ProductoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()

        response = create_response('success', 201, 'Producto creado', serializer.data)
        return Response(response, status=201)
    
    response = create_response('error', 400, 'Error al crear el producto', serializer.errors)
    return Response(response, status=400)


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def producto_list(request):
    productos = Producto.objects.all()
    serializer = ProductoSerializer(productos, many=True)

    response = create_response('success', 200, 'Lista de productos', serializer.data)
    return Response(response, status=200)


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def producto_detail(request, pk):
    try:
        producto = Producto.objects.get(id=pk)
    except Producto.DoesNotExist:
        response = create_response('error', 404, 'Producto no encontrado')
        return Response(response, status=404)
    serializer = ProductoSerializer(producto, many=False)

    response = create_response('success', 200, 'Producto encontrado', serializer.data)
    return Response(response, status=200)


@api_view(['PUT'])
# @permission_classes([IsAuthenticated])
def producto_update(request, pk):
    try:
        producto = Producto.objects.get(id=pk)
    except Producto.DoesNotExist:
        response = create_response('error', 404, 'Producto no encontrado')
        return Response(response, status=404)
    
    serializer = ProductoSerializer(instance=producto, data=request.data)
    if serializer.is_valid():
        serializer.save()

    response = create_response('success', 200, 'Producto actualizado', serializer.data)
    return Response(response, status=200)


@api_view(['DELETE'])
# @permission_classes([IsAuthenticated])
def producto_delete(request, pk):
    try:
        producto = Producto.objects.get(id=pk)
    except Producto.DoesNotExist:
        response = create_response('error', 404, 'Producto no encontrado')
        return Response(response, status=404)

    producto.activo = False

    response = create_response('success', 200, 'Producto eliminado', None)
    return Response(response, status=200)


@api_view(['POST'])
def generar_reporte(request):
    productos = Producto.objects.all()
    
    total_productos = productos.count()
    
    context = {
        'productos': productos,
        'total_productos': total_productos
    }
    
    # Renderizar el template HTML
    template = get_template('reporte_stock.html')  # Asegúrate de tener un template HTML adecuado
    html_content = template.render(context)
    
    # Convertir HTML a PDF
    pdf_data = convert_html_to_pdf(html_content)
    
    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_stock.pdf"'

    return response

def convert_html_to_pdf(html_content):
    result_file = BytesIO()
    pisa.CreatePDF(html_content, dest=result_file)
    pdf_data = result_file.getvalue()
    result_file.close()
    return pdf_data


@api_view(['POST'])
def generar_reporte_mas_vendidos(request):
    
    desde = request.data['desde']
    hasta = request.data['hasta']

    facturas = Factura.objects.all()
    facturas = facturas.filter(fecha_emision__range=[desde, hasta])

    productos = Producto.objects.all()
    productos = list(map(lambda producto: {
        'id': producto.id,
        'nombre': producto.nombre,
        'precio': producto.precio,
        'cantidad_vendida': 0
    }, productos))

    for producto in productos:
        producto['cantidad_vendida'] = 0
        for factura in facturas:
            items = ItemFactura.objects.all()
            items = items.filter(factura=factura)
            for item in items:
                if item.producto.id == producto['id']:
                    producto['cantidad_vendida'] += item.cantidad

    productos = sorted(productos, key=lambda producto: producto['cantidad_vendida'], reverse=True)

    total_vendidos = sum(map(lambda producto: producto['cantidad_vendida'], productos))

    context = {
        'desde': desde,
        'hasta': hasta,
        'productos': productos,
        'total_vendidos': total_vendidos
    }

    # Renderizar el template HTML
    template = get_template('reporte_mas_vendidos.html')

    html_content = template.render(context)

    # Convertir HTML a PDF
    pdf_data = convert_html_to_pdf(html_content)

    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_mas_vendidos.pdf"'

    return response


@api_view(['POST'])
def generar_reporte_de_utilidades(request):
    
    desde = request.data['desde']
    hasta = request.data['hasta']

    facturas = Factura.objects.all()
    facturas = facturas.filter(fecha_emision__range=[desde, hasta])

    productos = Producto.objects.all()
    productos = list(map(lambda producto: {
        'id': producto.id,
        'nombre': producto.nombre,
        'precio': producto.precio,
        'costo': producto.costo,
        'cantidad_vendida': 0,
        'total_vendido': 0,
        'total_comprado': 0,
        'utilidad': 0
    }, productos))

    for producto in productos:
        producto['cantidad_vendida'] = 0
        producto['total_vendido'] = 0
        producto['total_comprado'] = 0
        producto['utilidad'] = 0
        for factura in facturas:
            items = ItemFactura.objects.all()
            items = items.filter(factura=factura)
            for item in items:
                if item.producto.id == producto['id']:
                    producto['cantidad_vendida'] += item.cantidad
                    producto['total_vendido'] += item.cantidad * producto['precio']
                    producto['total_comprado'] += item.cantidad * producto['costo']

        producto['utilidad'] = producto['total_vendido'] - producto['total_comprado']

    total_utilidades = sum(map(lambda producto: producto['utilidad'], productos))

    context = {
        'desde': desde,
        'hasta': hasta,
        'productos': productos,
        'total_utilidades': total_utilidades
    }

    # Renderizar el template HTML
    template = get_template('reporte_de_utilidades.html')

    html_content = template.render(context)

    # Convertir HTML a PDF
    pdf_data = convert_html_to_pdf(html_content)

    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_de_utilidades.pdf"'

    return response
