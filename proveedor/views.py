from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from response import create_response
from .models import Proveedor
from .serializers import ProveedorSerializer
from io import BytesIO
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.template.loader import get_template
from factura.models import Factura


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
    

@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def generar_reporte(request):

    desde = request.data.get('desde')
    hasta = request.data.get('hasta')

    # reporte top 15 proveedores
    facturas = Factura.objects.all()
    facturas = facturas.filter(fecha_emision__range=[desde, hasta])
    proveedores = Proveedor.objects.all()

    proveedores_facturas = []
    for proveedor in proveedores:
        facturas_proveedor = facturas.filter(proveedor=proveedor)
        total_facturas = 0
        for factura in facturas_proveedor:
            total_facturas += factura.total
        proveedores_facturas.append({
            'proveedor': proveedor,
            'total_facturas': total_facturas
        })

    proveedores_facturas = sorted(proveedores_facturas, key=lambda x: x['total_facturas'], reverse=True)
    proveedores_facturas = proveedores_facturas[:15]

    # Crear PDF
    template = get_template('reporte_top_proveedores.html')
    context = {
        'desde': desde,
        'hasta': hasta,
        'proveedores_facturas': proveedores_facturas
    }

    html = template.render(context)
    pdf = convert_html_to_pdf(html)

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_top_proveedores.pdf"'

    return response
    

def convert_html_to_pdf(html_content):
    result_file = BytesIO()
    pisa.CreatePDF(html_content, dest=result_file)
    pdf_data = result_file.getvalue()
    result_file.close()
    return pdf_data
