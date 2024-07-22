from django.shortcuts import render
from rest_framework.decorators import api_view

from .models import Venta
from .serializers import VentaSerializer
from response import create_response
from rest_framework.response import Response
from xhtml2pdf import pisa
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from factura.models import Factura

# Create your views here.

@api_view(['Get'])
def venta_list(request):
    ventas = Venta.objects.all()
    serializer = VentaSerializer(ventas, many=True)

    response = create_response('success', 200, 'Lista de ventas', serializer.data)
    return Response(response, status=200)


@api_view(['POST'])
def generar_reporte(request):

    print(request.data)
    desde = request.data.get('desde', None)
    hasta = request.data.get('hasta', None)
    
    facturas = Factura.objects.all()

    if desde and hasta:
        facturas = facturas.filter(fecha_emision__range=[desde, hasta], operacion='venta')

    ventas = []

    for factura in facturas:
        ventas.extend(factura.venta_set.all()) 

    # set total
    ventas = list(map(lambda venta: {
        'id': venta.id,
        'cliente': venta.cliente.nombre,
        'producto': venta.producto.nombre,
        'cantidad': venta.cantidad,
        'precio': venta.producto.precio,
        'total': venta.cantidad * venta.producto.precio
    }, ventas))

    total = sum(map(lambda venta: venta['total'], ventas))

    context = {
        'desde': desde,
        'hasta': hasta,
        'ventas': ventas,
        'total': total
    }

    template = get_template('reporte_ventas.html')
    html_content = template.render(context)

    pdf_data = convert_html_to_pdf(html_content)

    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="reporte_ventas.pdf"'

    return response

def convert_html_to_pdf(html_content):
    result_file = BytesIO()
    pisa.CreatePDF(html_content, dest=result_file)
    pdf_data = result_file.getvalue()
    result_file.close()
    return pdf_data