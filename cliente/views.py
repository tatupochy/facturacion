from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from response import create_response
from .models import Cliente
from .serializers import ClienteSerializer
from io import BytesIO
import base64
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Create your views here.


@api_view(['GET'])
# #@permission_classes([IsAuthenticated])
def cliente_list(request):
    clientes = Cliente.objects.all()
    serializer = ClienteSerializer(clientes, many=True)

    response = create_response('success', 200, "Clientes obtenidos", serializer.data)
    return Response(response, status=200)

@api_view(['GET'])
# #@permission_classes([IsAuthenticated])
def cliente_detail(request, pk):
    try:
        cliente = Cliente.objects.get(id=pk)
    except Cliente.DoesNotExist:
        response = create_response('error', 404, "Cliente no encontrado", None)
        return Response(response, status=404)
    
    serializer = ClienteSerializer(cliente, many=False)

    response = create_response('success', 200, "Cliente obtenido", serializer.data)
    return Response(response, status=200)

@api_view(['POST'])
# #@permission_classes([IsAuthenticated])
def cliente_create(request):
    serializer = ClienteSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()

        response = create_response('created', 201, 'Cliente creado', serializer.data)
        return Response(response, status=201)
    
    response = create_response('error', 400, 'Error al crear cliente', serializer.errors)
    return Response(response, status=400)

@api_view(['PUT'])
# #@permission_classes([IsAuthenticated])
def cliente_update(request, pk):
    try:
        cliente = Cliente.objects.get(id=pk)
    except Cliente.DoesNotExist:
        response = create_response('error', 404, 'Cliente no encontrado', None)
        return Response(response, status=404)
    
    serializer = ClienteSerializer(instance=cliente, data=request.data)
    if serializer.is_valid():
        serializer.save()

        response = create_response('success', 200, 'Cliente actualizado', serializer.data)
        return Response(response, status=200)
    
    response = create_response('error', 400, 'Error al actualizar cliente', serializer.errors)
    return Response(response, status=400)

@api_view(['DELETE'])
# #@permission_classes([IsAuthenticated])
def cliente_delete(request, pk):
    try:
        cliente = Cliente.objects.get(id=pk)
        if cliente:
            cliente.delete()
    except Cliente.DoesNotExist:
        response = create_response('error', 404, 'Cliente no encontrado', None)
        return Response(response, status=404)

    response = create_response('success', 200, 'Cliente eliminado', None)
    return Response(response, status=200)   

@api_view(['GET'])
# #@permission_classes([IsAuthenticated])
def generar_reporte(request):
    clientes = Cliente.objects.all()

    # Generar el PDF utilizando ReportLab
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.drawString(100, 750, 'Reporte de clientes')
    y = 700
    for cliente in clientes:
        y -= 20
        c.drawString(100, y, f'Nombre: {cliente.nombre}')
        y -= 20
        c.drawString(100, y, f'Email: {cliente.email}')
        y -= 20
        c.drawString(100, y, f'Telefono: {cliente.telefono}')
        y -= 20
        c.drawString(100, y, f'Direccion: {cliente.direccion}')
        y -= 20
        c.drawString(100, y, '--------------------------------------')
    c.save()

    # Convertir el contenido del PDF a base64
    pdf = buffer.getvalue()
    base64_pdf = base64.b64encode(pdf).decode('utf-8')

    # Crear la respuesta JSON con el contenido base64
    response = create_response('success', 200, 'Reporte generado', base64_pdf)
    return Response(response, status=200)