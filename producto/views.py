from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from response import create_response
from .models import Producto
from .serializers import ProductoSerializer
from io import BytesIO
import base64
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


# Create your views here.

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def producto_create(request):
    serializer = ProductoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()

        response = create_response('success', 'Producto creado', serializer.data)
        return Response(response, status=201)
    
    response = create_response('error', 'Error al crear producto', serializer.errors)
    return Response(response, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def producto_list(request):
    productos = Producto.objects.all()
    serializer = ProductoSerializer(productos, many=True)

    response = create_response('success', 'Productos listados', serializer.data)
    return Response(response, status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def producto_detail(request, pk):
    producto = Producto.objects.get(id=pk)
    serializer = ProductoSerializer(producto, many=False)

    response = create_response('success', 'Producto listado', serializer.data)
    return Response(response, status=200)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def producto_update(request, pk):
    producto = Producto.objects.get(id=pk)
    serializer = ProductoSerializer(instance=producto, data=request.data)
    if serializer.is_valid():
        serializer.save()

    response = create_response('success', 'Producto actualizado', serializer.data)
    return Response(response, status=200)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def producto_delete(request, pk):
    producto = Producto.objects.get(id=pk)
    if producto:
        producto.delete()

        response = create_response('success', 'Producto eliminado', None)
        return Response(response, status=200)
    
    response = create_response('error', 'Producto no encontrado', None)
    return Response(response, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generar_reporte(request):
    productos = Producto.objects.all()
    response = BytesIO()
    pdf = canvas.Canvas(response, pagesize=letter)
    pdf.drawString(100, 800, 'Reporte de Productos')
    pdf.drawString(100, 780, 'Lista de productos')
    pdf.drawString(100, 760, 'ID - Nombre - Precio - Stock')
    y = 740
    for producto in productos:
        pdf.drawString(100, y, f'{producto.id} - {producto.nombre} - {producto.precio}')
        y -= 20
    pdf.showPage()
    pdf.save()
    response.seek(0)
    pdf_base64 = base64.b64encode(response.getvalue()).decode('utf-8')
    response.close()

    response = create_response('success', 'Reporte generado', pdf_base64)
    return Response(response, status=200)

