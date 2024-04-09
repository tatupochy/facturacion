from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Producto
from .serializers import ProductoSerializer


# Create your views here.

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def producto_create(request):
    serializer = ProductoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)    
    return Response(serializer.errors)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def producto_list(request):
    productos = Producto.objects.all()
    serializer = ProductoSerializer(productos, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def producto_detail(request, pk):
    producto = Producto.objects.get(id=pk)
    serializer = ProductoSerializer(producto, many=False)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def producto_update(request, pk):
    producto = Producto.objects.get(id=pk)
    serializer = ProductoSerializer(instance=producto, data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def producto_delete(request, pk):
    producto = Producto.objects.get(id=pk)
    producto.delete()
    return Response('Producto eliminado')

