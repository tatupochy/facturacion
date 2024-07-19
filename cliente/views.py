from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from response import create_response
from .models import Cliente
from factura.models import Factura
from django.template.loader import get_template
from .serializers import ClienteSerializer
from io import BytesIO
from xhtml2pdf import pisa
from django.http import HttpResponse

# Create your views here.


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def cliente_list(request):
    clientes = Cliente.objects.all()
    serializer = ClienteSerializer(clientes, many=True)

    response = create_response('success', 200, "Clientes obtenidos", serializer.data)
    return Response(response, status=200)


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
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
# @permission_classes([IsAuthenticated])
def cliente_create(request):
    serializer = ClienteSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()

        response = create_response('success', 200, 'Cliente creado', serializer.data)
        return Response(response, status=200)
    
    response = create_response('error', 400, 'Error al crear cliente', serializer.errors)
    return Response(response, status=400)


@api_view(['PUT'])
# @permission_classes([IsAuthenticated])
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
# @permission_classes([IsAuthenticated])
def cliente_delete(request, pk):
    try:
        cliente = Cliente.objects.get(id=pk)
        if cliente:
            cliente.activo = False
    except Cliente.DoesNotExist:
        response = create_response('error', 404, 'Cliente no encontrado', None)
        return Response(response, status=404)

    response = create_response('success', 200, 'Cliente eliminado', None)
    return Response(response, status=200)   


@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def generar_reporte(request):

    desde = request.data.get('desde')
    hasta = request.data.get('hasta')

    # reporte top 15 clientes
    facturas = Factura.objects.all()
    facturas = facturas.filter(fecha_emision__range=[desde, hasta])
    clientes = Cliente.objects.all()

    clientes_facturas = []
    for cliente in clientes:
        facturas_cliente = facturas.filter(cliente=cliente)
        total_facturas = 0
        for factura in facturas_cliente:
            total_facturas += factura.total
        clientes_facturas.append({
            'cliente': cliente,
            'total_facturas': total_facturas
        })

    clientes_facturas = sorted(clientes_facturas, key=lambda x: x['total_facturas'], reverse=True)
    clientes_facturas = clientes_facturas[:15]

    # Crear PDF
    template = get_template('reporte_top_clientes.html')
    context = {
        'desde': desde,
        'hasta': hasta,
        'clientes_facturas': clientes_facturas
    }

    html = template.render(context)
    pdf = convert_html_to_pdf(html)

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_top_clientes.pdf"'

    return response
    

def convert_html_to_pdf(html_content):
    result_file = BytesIO()
    pisa.CreatePDF(html_content, dest=result_file)
    pdf_data = result_file.getvalue()
    result_file.close()
    return pdf_data