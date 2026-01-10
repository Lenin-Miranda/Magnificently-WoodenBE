from django.urls import path
from .views import (
    OrderDetailView,
    OrderListView,
    AdminOrderDetailView,
    AdminOrderListView,
)

app_name = 'orders'

urlpatterns = [

    #------ PUBLIC URLS ------

    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/<int:id>/', OrderDetailView.as_view(), name='order-detail'),

   #------ ADMIN URLS ------

    path('admin/orders/', AdminOrderListView.as_view(), name='admin-order-list'),
    path('admin/orders/<int:id>/', AdminOrderDetailView.as_view(), name='admin-order-detail'),
]
