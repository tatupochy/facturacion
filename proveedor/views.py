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
@permission_classes([IsAuthenticated])
def proveedor_create(request):
    serializer = ProveedorSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()

        response = create_response('success', 'Proveedor creado', serializer.data)
        return Response(response, status=status.HTTP_201_CREATED)
    
    response = create_response('error', 'Error al crear proveedor', serializer.errors)
    return Response(response, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def proveedor_list(request):
    proveedores = Proveedor.objects.all()
    serializer = ProveedorSerializer(proveedores, many=True)

    response = create_response('success', 'Lista de proveedores', serializer.data)
    return Response(response, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def proveedor_detail(request, pk):
    proveedor = Proveedor.objects.get(id=pk)
    serializer = ProveedorSerializer(proveedor, many=False)

    response = create_response('success', 'Proveedor listado', serializer.data)
    return Response(response, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def proveedor_update(request, pk):
    proveedor = Proveedor.objects.get(id=pk)
    serializer = ProveedorSerializer(instance=proveedor, data=request.data)
    if serializer.is_valid():
        serializer.save()

        response = create_response('success', 'Proveedor actualizado', serializer.data)
        return Response(response, status=status.HTTP_200_OK)
    
    response = create_response('error', 'Error al actualizar proveedor', serializer.errors)
    return Response(response, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def proveedor_delete(request, pk):
    proveedor = Proveedor.objects.get(id=pk)
    proveedor.delete()
    if proveedor:
        response = create_response('success', 'Proveedor eliminado', None)
        return Response(response, status=status.HTTP_200_OK)
    
    response = create_response('error', 'Proveedor no encontrado', None)
    return Response(response, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
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

    response = create_response('success', 'Reporte de proveedores', pdf_base64)
    return Response(response, status=status.HTTP_200_OK)

