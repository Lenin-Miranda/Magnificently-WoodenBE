from django.urls import path
from .views import (
    ProductViewSet,
    ProductDetailView,
    CategoryViewSet,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
    ProductImageUploadView,
    ProductImageDeleteView,
)

urlpatterns = [
    # PUBLIC
    path("", ProductViewSet.as_view(), name='product-list'),
    path("<slug:slug>/", ProductDetailView.as_view(), name='product-detail'),
    path("categories/all/", CategoryViewSet.as_view(), name='category-list'),

    # ADMIN
    path("admin/create/", ProductCreateView.as_view(), name='product-create'),
    path("admin/update/<int:id>/", ProductUpdateView.as_view(), name='product-update'),
    path("admin/delete/<int:id>/", ProductDeleteView.as_view(), name='product-delete'),

    # ADMIN: IMAGES
    path("admin/<int:product_id>/images/", ProductImageUploadView.as_view(), name='product-image-upload'),
    path("admin/images/<int:id>/delete/", ProductImageDeleteView.as_view(), name='product-image-delete'),
]


