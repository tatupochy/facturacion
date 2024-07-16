from django.shortcuts import render
from rest_framework.decorators import api_view

from .models import Compra
from .serializers import CompraSerializer
from response import create_response
from rest_framework.response import Response

# Create your views here.

@api_view(['Get'])
def compra_list(request):
    compras = Compra.objects.all()
    serializer = CompraSerializer(compras, many=True)

    response = create_response('success', 200, 'Lista de compras', serializer.data)
    return Response(response, status=200)