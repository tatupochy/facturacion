from django.shortcuts import render
from rest_framework.decorators import api_view

from .models import Venta
from .serializers import VentaSerializer
from response import create_response
from rest_framework.response import Response

# Create your views here.

@api_view(['Get'])
def venta_list(request):
    ventas = Venta.objects.all()
    serializer = VentaSerializer(ventas, many=True)

    response = create_response('success', 200, 'Lista de ventas', serializer.data)
    return Response(response, status=200)