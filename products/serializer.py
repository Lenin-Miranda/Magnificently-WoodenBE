from rest_framework import serializers
from .models import Product, Category, ProductImage

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        required=True
    )
    slug = serializers.SlugField(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'price', 'inStock',
            'main_image', 'isActive', 'isFeatured', 'rating', 'status',
            'created_at', 'updated_at', 'category', 'images'
        ]

    def to_representation(self, instance):
        """On read, return full category object instead of just the ID"""
        representation = super().to_representation(instance)
        representation['category'] = CategorySerializer(instance.category).data if instance.category else None
        return representation