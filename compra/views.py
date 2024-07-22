from io import BytesIO
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.decorators import api_view
from django.template.loader import get_template

from factura.models import Factura
from .models import Compra
from .serializers import CompraSerializer
from response import create_response
from rest_framework.response import Response
from xhtml2pdf import pisa

# Create your views here.

@api_view(['Get'])
def compra_list(request):
    compras = Compra.objects.all()
    serializer = CompraSerializer(compras, many=True)

    response = create_response('success', 200, 'Lista de compras', serializer.data)
    return Response(response, status=200)


@api_view(['POST'])
def generar_reporte(request):

    print(request.data)
    desde = request.data.get('desde', None)
    hasta = request.data.get('hasta', None)
    
    facturas = Factura.objects.all()

    if desde and hasta:
        facturas = facturas.filter(fecha_emision__range=[desde, hasta], operacion='compra')

    compras = []

    for factura in facturas:
        compras.extend(factura.compra_set.all()) 

    total_cantidad = sum(map(lambda compra: compra.cantidad, compras))
    total_total = sum(map(lambda compra: compra.cantidad * compra.producto.precio, compras))

    # set total
    compras = list(map(lambda compra: {
        'id': compra.id,
        'proveedor': compra.proveedor.nombre,
        'producto': compra.producto.nombre,
        'cantidad': compra.cantidad,
        'precio': compra.producto.precio,
        'total': compra.cantidad * compra.producto.precio
    }, compras))

    context = {
        'desde': desde,
        'hasta': hasta,
        'compras': compras,
        'total_cantidad': total_cantidad,
        'total_total': total_total
    }

    template = get_template('reporte_compras.html')
    html_content = template.render(context)

    pdf_data = convert_html_to_pdf(html_content)

    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="reporte_compras.pdf"'

    return response

def convert_html_to_pdf(html_content):
    result_file = BytesIO()
    pisa.CreatePDF(html_content, dest=result_file)
    pdf_data = result_file.getvalue()
    result_file.close()
    return pdf_data
