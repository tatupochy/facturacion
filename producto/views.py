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


@api_view(['GET'])
def generar_reporte(request):
    productos = Producto.objects.all()
    context = {
        'productos': productos
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
