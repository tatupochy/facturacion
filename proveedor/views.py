from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from response import create_response
from .models import Proveedor
from .serializers import ProveedorSerializer
from io import BytesIO
import base64
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Create your views here.


@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def proveedor_create(request):
    serializer = ProveedorSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()

        response = create_response('success', 201, 'Proveedor creado', serializer.data)
        return Response(response, status= 201)
    
    response = create_response('error', 400, 'Error al crear proveedor', serializer.errors)
    return Response(response, status= 400)


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def proveedor_list(request):
    proveedores = Proveedor.objects.all()
    serializer = ProveedorSerializer(proveedores, many=True)

    response = create_response('success', 200, 'Lista de proveedores', serializer.data)
    return Response(response, status=200)


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def proveedor_detail(request, pk):
    try:
        proveedor = Proveedor.objects.get(id=pk)
    except Proveedor.DoesNotExist:
        response = create_response('error', 404, 'Proveedor no encontrado')
        return Response(response, status= 404)
    
    serializer = ProveedorSerializer(proveedor, many=False)

    response = create_response('success', 200, 'Proveedor encontrado', serializer.data)
    return Response(response, status= 200)


@api_view(['PUT'])
# @permission_classes([IsAuthenticated])
def proveedor_update(request, pk):
    try:
        proveedor = Proveedor.objects.get(id=pk)
    except Proveedor.DoesNotExist:
        response = create_response('error', 404, 'Proveedor no encontrado')
        return Response(response, status=404)
    
    serializer = ProveedorSerializer(instance=proveedor, data=request.data)
    if serializer.is_valid():
        serializer.save()

        response = create_response('success', 200, 'Proveedor actualizado', serializer.data)
        return Response(response, status=200)
    else:
        response = create_response('error', 400, 'Error al actualizar proveedor', serializer.errors)
        return Response(response, status=400)


@api_view(['DELETE'])
# @permission_classes([IsAuthenticated])
def proveedor_delete(request, pk):
    try:
        proveedor = Proveedor.objects.get(id=pk)
    except Proveedor.DoesNotExist:
        response = create_response('error', 404, 'Proveedor no encontrado')
        return Response(response, status=status.HTTP_404_NOT_FOUND)
    
    proveedor.activo = False

    response = create_response('success', 200, 'Proveedor eliminado')
    return Response(response, status=200)
    

@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def generar_reporte(request):
    proveedores = Proveedor.objects.all()
    
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.drawString(100, 750, 'Reporte de proveedores')
    y = 700
    for proveedor in proveedores:
        pdf.drawString(100, y, proveedor.nombre)
        pdf.drawString(200, y, proveedor.direccion)
        pdf.drawString(300, y, proveedor.telefono)
        pdf.drawString(400, y, proveedor.ruc)
        y -= 20

    pdf.showPage()
    pdf.save()
    pdf_buffer = buffer.getvalue()
    buffer.close()
    pdf_base64 = base64.b64encode(pdf_buffer).decode('utf-8')

    response = create_response('success', 200, 'Reporte generado', {'pdf': pdf_base64})
    return Response(response, status=200)

