from .models import Order, OrderItem
from .serializer import AdminOrderSerializer, OrderSerializer, OrderItemSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser


#----- USER VIEWS -----
from rest_framework import status

class OrderListView(generics.ListAPIView):
    '''
    List all orders for the logged in user
    '''

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')


class OrderDetailView(generics.RetrieveAPIView):
    '''
    Retrieve a specific order for the logged in user
    '''

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')

    lookup_field = 'id'

#----- ADMIN VIEWS -----
from rest_framework.pagination import PageNumberPagination

class AdminOrderListView(generics.ListAPIView):
    '''
    List all orders (admin only)
    '''

    queryset = Order.objects.select_related('user').prefetch_related('items').all()
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser]
    pagination_class = PageNumberPagination

class AdminOrderDetailView(generics.RetrieveUpdateAPIView):
    '''
    Retrieve / update a specific order (admin only)
    '''

    queryset = Order.objects.select_related('user').prefetch_related('items').all()
    serializer_class = AdminOrderSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'

class AdminOrderItemListView(generics.ListAPIView):
    '''
    List all order items (admin only)
    '''

    queryset = OrderItem.objects.select_related('order', 'product').all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAdminUser]

class AdminOrderItemDetailView(generics.RetrieveAPIView):
    '''
    Retrieve a specific order item (admin only)
    '''

    queryset = OrderItem.objects.select_related('order', 'product').all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'
