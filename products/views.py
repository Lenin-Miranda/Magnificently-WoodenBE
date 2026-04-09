from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from .models import Product, Category, ProductImage
from .serializer import ProductSerializer, CategorySerializer, ProductImageSerializer

# ------ PUBLIC VIEWS ------

class ProductViewSet(generics.ListCreateAPIView):
    queryset = Product.objects.filter(isActive=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(isActive=True)
    serializer_class = ProductSerializer
    lookup_field = 'slug'
    permission_classes = [AllowAny]

class CategoryViewSet(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

# ------ ADMIN VIEWS ------

class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        product = serializer.save()
        # Handle multiple images sent as 'images' in multipart/form-data
        images = self.request.FILES.getlist('images')
        for image in images:
            ProductImage.objects.create(product=product, image=image)

class ProductUpdateView(generics.UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAdminUser]
    lookup_field = 'id'

    def perform_update(self, serializer):
        product = serializer.save()
        # If new images are sent, add them to the product
        images = self.request.FILES.getlist('images')
        for image in images:
            ProductImage.objects.create(product=product, image=image)

class ProductDeleteView(generics.DestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'

# ------ ADMIN: PRODUCT IMAGES ------

class ProductImageUploadView(generics.CreateAPIView):
    """Upload one or more images to a specific product."""
    serializer_class = ProductImageSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAdminUser]

    def create(self, request, *args, **kwargs):
        product_id = self.kwargs.get('product_id')
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        images = request.FILES.getlist('images')
        if not images:
            return Response(
                {'error': 'No images provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        created_images = []
        for image in images:
            alt_text = request.data.get('alt_text', '')
            img = ProductImage.objects.create(
                product=product, image=image, alt_text=alt_text
            )
            created_images.append(img)

        serializer = ProductImageSerializer(created_images, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProductImageDeleteView(generics.DestroyAPIView):
    """Delete a specific image by its ID."""
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'
