from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.authentication import TokenAuthentication

from .models import Product
from .serializers import ProductSerializer


class ProductListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/products/  -> public, paginated list ordered by id
    POST /api/products/  -> requires `Authorization: Token <token>`
    """
    queryset = Product.objects.all().order_by('id')
    serializer_class = ProductSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
