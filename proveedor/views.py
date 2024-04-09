from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Proveedor
from .serializers import ProveedorSerializer


# Create your views here.

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def proveedor_create(request):
    serializer = ProveedorSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def proveedor_list(request):
    proveedores = Proveedor.objects.all()
    serializer = ProveedorSerializer(proveedores, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def proveedor_detail(request, pk):
    proveedor = Proveedor.objects.get(id=pk)
    serializer = ProveedorSerializer(proveedor, many=False)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def proveedor_update(request, pk):
    proveedor = Proveedor.objects.get(id=pk)
    serializer = ProveedorSerializer(instance=proveedor, data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def proveedor_delete(request, pk):
    proveedor = Proveedor.objects.get(id=pk)
    proveedor.delete()
    return Response('Proveedor eliminado')

